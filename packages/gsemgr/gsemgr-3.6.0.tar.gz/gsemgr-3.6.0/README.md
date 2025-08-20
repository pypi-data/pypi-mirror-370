# gsemgr

GSE's version of [mcumgr](https://docs.zephyrproject.org/latest/services/device_mgmt/mcumgr.html). Faster and with more functionality:

- Sane multi-core firmware updates.
- SMP extensions.
- Run Python code on the target and check its output.

# Python tools

The various packaging operations (adding and checking dependencies, building wheels/sdists and so on) are done with [uv](https://github.com/astral-sh/uv) because it simplifies the workflow. That is not a requirement though, the usual Python tools should be usable without issues.
