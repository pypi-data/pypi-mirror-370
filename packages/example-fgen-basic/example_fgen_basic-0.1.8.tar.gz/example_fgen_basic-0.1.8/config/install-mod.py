#!/usr/bin/env python3
"""
Originally copied from: https://github.com/toml-f/toml-f/blob/main/config/install-mod.py

Using the MIT License, copyright notice below
(from https://github.com/toml-f/toml-f/blob/main/LICENSE-MIT)

Copyright (c) 2019-2021 Sebastian Ehlert

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
"""

from os import environ, listdir, makedirs
from os.path import exists, isdir, join
from shutil import copy
from sys import argv

build_dir = environ["MESON_BUILD_ROOT"]

if "MESON_INSTALL_DESTDIR_PREFIX" in environ:
    install_dir = environ["MESON_INSTALL_DESTDIR_PREFIX"]

else:
    install_dir = environ["MESON_INSTALL_PREFIX"]

include_dir = argv[1] if len(argv) > 1 else "include"
module_dir = join(install_dir, include_dir)

modules = []
for d in listdir(build_dir):
    bd = join(build_dir, d)
    if isdir(bd):
        for f in listdir(bd):
            if f.endswith(".mod"):
                modules.append(join(bd, f))

if not exists(module_dir):
    makedirs(module_dir)

for mod in modules:
    print("Installing (from custom python script)", mod, "to", module_dir)
    copy(mod, module_dir)
