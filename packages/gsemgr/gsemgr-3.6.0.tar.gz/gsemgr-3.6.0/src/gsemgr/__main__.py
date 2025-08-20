# "mcumgr" in Python, with specific optimizations for our source tree

# GSE Proprietary Software License
# Copyright (c) 2025 Global Satellite Engineering, LLC. All rights reserved.
# This software and associated documentation files (the "Software") are the proprietary and confidential information of Global Satellite Engineering, LLC ("GSE"). The Software is provided solely for the purpose of operating applications distributed by GSE and is subject to the following conditions:

# 1. NO RIGHTS GRANTED: This license does not grant any rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell the Software.
# 2. RESTRICTED ACCESS: You may only access the Software as part of a GSE application package and only to the extent necessary for operation of that application package.
# 3. PROHIBITION ON REVERSE ENGINEERING: You may not reverse engineer, decompile, disassemble, or attempt to derive the source code of the Software.
# 4. PROPRIETARY NOTICES: You must retain all copyright, patent, trademark, and attribution notices present in the Software.
# 5. NO WARRANTIES: The Software is provided "AS IS", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement.
# 6. LIMITATION OF LIABILITY: In no event shall GSE be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the Software or the use or other dealings in the Software.
# 7. TERMINATION: This license will terminate automatically if you fail to comply with any of the terms and conditions of this license. Upon termination, you must destroy all copies of the Software in your possession.

# THE SOFTWARE IS PROTECTED BY UNITED STATES COPYRIGHT LAW AND INTERNATIONAL TREATY. UNAUTHORIZED REPRODUCTION OR DISTRIBUTION IS SUBJECT TO CIVIL AND CRIMINAL PENALTIES.

import sys
import argparse
from gse_utils import utils
from gse_utils import ser_driver
from gse_utils import detect_ports
from . import smp_commands
from . import gse_commands
from . import ftp_server
from . import http_server
from . import terminal
from .smp_exceptions import *
import traceback
from . import common
import importlib
import os

#######################################################################################################################
# Local functions and data

# Display package version
def print_version(_, __):
    try:
        print(importlib.metadata.version(__name__.split(".")[0]))
    except:
        utils.error("Unable to find package version")

# Display configuration path
def print_config_path(_, args):
    print(utils.get_config_file_path(args.cfg_path, must_exist=False))

# "image" command has further sub-commands
img_actions = {
    "list": {"handler": smp_commands.cmd_image_list, "help": "list firmware images", "args": smp_commands.image_list_args},
    "upload": {"handler": smp_commands.cmd_image_upload, "help": "upload firmware image", "args": smp_commands.image_upload_args},
    "erase": {"handler": smp_commands.cmd_image_erase, "help": "erase firmware image. USE WITH CARE.", "args": smp_commands.image_erase_args},
    "activate": {"handler": smp_commands.cmd_image_activate, "help": "activate a firmware image", "args": smp_commands.image_activate_args},
}
# "file" command has further sub-commands
file_actions = {
    "status": {"handler": smp_commands.cmd_file_status, "help": "get file status", "args": smp_commands.file_status_args},
    "download": {"handler": smp_commands.cmd_file_download, "help": "download file from target", "args": smp_commands.file_download_args,
                 "cleanup": smp_commands.file_up_dl_cleanup},
    "upload": {"handler": smp_commands.cmd_file_upload, "help": "upload file to target", "args": smp_commands.file_upload_args,
               "cleanup": smp_commands.file_up_dl_cleanup},
    "cat": {"handler": smp_commands.cmd_file_cat, "help": "display target file contents", "args": smp_commands.file_cat_args,
            "cleanup": smp_commands.file_up_dl_cleanup},
}
# "prop" command has further sub-commands
prop_actions = {
    "get": {"handler": gse_commands.cmd_prop_get, "help": "get the value of a property or all properties",
            "args": gse_commands.prop_get_args},
    "set": {"handler": gse_commands.cmd_prop_set, "help": "set the value of a property", "args": gse_commands.prop_set_args}
}

# "extro" commands has further sub-commands
extro_actions = {
    "upload": {"handler": gse_commands.cmd_extro_upload, "help": "upload a ROMFS image to the external flash",
               "args": gse_commands.extro_upload_args},
    "erase": {"handler": gse_commands.cmd_extro_erase, "help": "erase the external ROMFS image if it exists"}
}

# Mapping between supported actions and their handlers
# Each key has two entries: the handler function (mandatory) and the "extra args" function which can be used to add
# action-specific arguments to the command line (optional)
actions = {
    "reset": {"handler": smp_commands.cmd_reset, "help": "reset board"},
    "echo": {"handler": smp_commands.cmd_echo, "help": "echo back a string", "args": smp_commands.echo_args},
    "threads": {"handler": smp_commands.cmd_threads, "help": "get info about the running threads", "args": smp_commands.threads_args},
    "image": {"sub": img_actions, "help": "image commands", "target": "img_action"},
    "file": {"sub": file_actions, "help": "file commands", "target": "file_action"},
    "prop": {"sub": prop_actions, "help": "read and write properties", "target": "prop_action"},
    "runpy": {"handler": gse_commands.cmd_run_python, "help": "run the given Python code and display its output",
        "args": gse_commands.runpy_args},
    "ftpd": {"handler": ftp_server.cmd_ftpd, "help": "access the device file systems over FTP", "args": ftp_server.ftpd_args},
    "httpd": {"handler": http_server.cmd_httpd, "help": "Start the HTTP server", "args": http_server.httpd_args},
    "version": {"handler": print_version, "help": "Display package version", "needs_serial": False},
    "config_path": {"handler": print_config_path, "help": "Display configuration file path", "needs_serial": False},
    "extro": {"sub": extro_actions, "help": "external ROMFS commands", "target": "extro_actions"},
    "console": {"handler": terminal.cmd_console, "help": "Connect to the device console with a terminal emulator",
        "args": terminal.console_args},
    "logs": {"handler": terminal.cmd_logs, "help": "View the devive logs in real time", "args": terminal.logs_args},
    "list": {"handler": gse_commands.cmd_list_devices, "help": "List autodetected devices", "needs_serial": False},
}

# Create the parser arguments for the given command map
def create_args(parser, cmds, target):
    subparsers = parser.add_subparsers(dest=target, required=True)
    for a, v in cmds.items():
        temp_p = subparsers.add_parser(a, help=cmds[a]["help"])
        v.get("args", lambda _: None)(temp_p)
        if "sub" in v: # recursive call to create this "sublist" of actions
            create_args(temp_p, v["sub"], v["target"])

# Return the port of the given kind (which can be "mgmt" or "console") or None if the port was not found.
# Ports are located as follows:
#    - if speicifed in the command line, that value is used
#    - otherwise, if it is present in the configuration file, that value is used
#    - otherwise, an attempt is made to detect the port automatically using the optional serial number from the command line
def get_port(kind, cmdline_port, cmdline_sernum, cfg):
    res = None
    if cmdline_port != None:
        return cmdline_port
    if cfg:
        res = utils.get_config_entry(cfg, "ports", kind)
    if res == None: # attempt to detect ports automatically
        global detected_devices
        try:
            detected = detect_ports.detect()
        except:
            detected = {}
        if not detected:
            utils.warning("No serial ports detected")
        else:
            if (cmdline_sernum != None) and (not cmdline_sernum in detected):
                utils.warning(f"Can't find a device with serial number {cmdline_sernum}, port detextion failed")
            else:
                if (len(detected) > 1) and (cmdline_sernum != None):
                    utils.warning("Found multiple devices, serial port detection failed. Consider using --sernum")
                else:
                    ser = cmdline_sernum if cmdline_sernum != None else list(detected.keys())[0]
                    res = detected[ser][kind]
                    if res != None:
                        utils.debug(f"Found {kind} port {res} for unit with serial number {ser}")
    return res

#######################################################################################################################
# Public interface

# Entry point
def main():
    parser = argparse.ArgumentParser(description='Remote resource manager for GSatMicro v2 devices.')
    parser.add_argument("-v", "--verbose", help="Verbose messages (can be given more than once)", action="count", default=0)
    parser.add_argument("-p", "--port", help="Port to use", default=None)
    parser.add_argument("--sernum", help="Use the device with the given serial number", required=False, default=None)
    parser.add_argument("--cfg-path", help="Path to config file", default=None)
    create_args(parser, actions, "action")
    # Parse arguments
    args = parser.parse_args()
    utils.set_debug_level(args.verbose)

    # Load configuration if available, create a default one if not found
    cfg_path = utils.get_config_file_path(args.cfg_path, must_exist=False)
    if not os.path.isfile(cfg_path):
        utils.info("Creating empty configuration file at {}".format(cfg_path))
        with open(cfg_path, "wt") as f:
            f.write("[ports]\n")
    cfg = utils.read_config(args.cfg_path, must_exist=True)

    # Run action
    err = True
    try:
        entry = actions[args.action]
        if "sub" in entry:
            entry = entry["sub"][getattr(args, entry["target"])]
        cleanup = entry.get("cleanup", None)
        # The "terminal" command needs to communicate with the console serial port, all the other commands use the gsemgr port
        ser = None
        if entry.get("needs_serial", True):
            if args.action == "console":
                port_kind = "console"
            elif args.action == "logs":
                port_kind = "logs"
            else:
                port_kind = "mgmt"
            port_name = get_port(port_kind, args.port, args.sernum, cfg)
            if port_name == None:
                utils.fatal("Serial port not found")
            else:
                ser = ser_driver.SerialHandler(port_name, 115200, echo_rx=False, echo_tx=False)
                ser.set_auto_close(True)
        common.init(ser, args, cfg)
        entry["handler"](ser, args)
        err = False
    except (FrameReadError, InvalidFrameError, InvalidResponseError, InvalidResponseData) as e:
        utils.error("An SMP exception of type {} has occured: {}".format(type(e).__name__, str(e)))
    except Exception as e:
        utils.error(traceback.format_exc())
    finally:
        if cleanup is not None: # execute cleanup function if needed
            cleanup(ser, args)
    if err:
        sys.exit(1)
