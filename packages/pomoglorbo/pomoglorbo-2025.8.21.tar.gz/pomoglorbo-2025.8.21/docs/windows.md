<!--
SPDX-FileCopyrightText: 2023 Justus Perlwitz
SPDX-FileCopyrightText: 2024 Justus Perlwitz
SPDX-FileCopyrightText: 2021-2023 Bhatihya Perera

SPDX-License-Identifier: MIT
-->

---
title: Windows support in pomoglorbo
---

Windows is not supported or tested. The original pydoro included the following
files:

`make_exe.cmd`

```bath
@echo off
pyinstaller pomoglorbo_tui.py -n pomoglorbo --onefile --add-data ".\pomoglorbo\core\b15.wav;." --add-data ".\.venv\Lib\site-packages\wcwidth;wcwidth" --hidden-import="pkg_resources.py2_warn"
```

```txt
prompt-toolkit==3.0.39
pyinstaller==5.13.0
twine==4.0.2
```
