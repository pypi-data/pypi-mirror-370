# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

def version_cmp(ver1, ver2):
    """ comparing version
        rt 1, -1, 0
    """
    if ver1 == ver2:
        return 0
    ver1 = ver1.split('.')
    ver2 = ver2.split('.')
    i = 0
    while True:
        if i >= len(ver1) and i >= len(ver2):
            return 0
        if i >= len(ver1) and i < len(ver2):
            return -1
        if i >= len(ver2) and i < len(ver1):
            return 1
        if ver1[i].isdigit() and ver2[i].isdigit():
            c1 = int(ver1[i])
            c2 = int(ver2[i])
            if c1 > c2:
                return 1
            elif c1 < c2:
                return -1
        elif ver1[i].isdigit():
            return 1
        elif ver2[i].isdigit():
            return -1
        else:
            return 0
        i += 1