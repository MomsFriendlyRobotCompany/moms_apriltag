![](https://github.com/MomsFriendlyRobotCompany/moms_apriltag/blob/master/example/apriltag_target.png?raw=true)

# Apriltag Camera Calibration Board Generator
![CheckPackage](https://github.com/MomsFriendlyRobotCompany/moms_apriltag/workflows/CheckPackage/badge.svg)
![GitHub](https://img.shields.io/github/license/MomsFriendlyRobotCompany/moms_apriltag)
[![Latest Version](https://img.shields.io/pypi/v/moms_apriltag.svg)](https://pypi.python.org/pypi/moms_apriltag/)
[![image](https://img.shields.io/pypi/pyversions/moms_apriltag.svg)](https://pypi.python.org/pypi/moms_apriltag)
[![image](https://img.shields.io/pypi/format/moms_apriltag.svg)](https://pypi.python.org/pypi/moms_apriltag)
![PyPI - Downloads](https://img.shields.io/pypi/dm/moms_apriltag?color=aqua)

Why? There didn't really seem to be an easy way to do this IMHO.

## Install

```
pip install moms_apriltag
```

## Usage

This package create a simple numpy image that can then be saved
to a PNG or JPEG image and printed.

Supported families: `tag16h5`, `tag25h9`, `tag36h10`, `tag36h11`

```
#!/usr/bin/env python3
import moms_apriltag as apt
import imageio


if __name__ == '__main__':
    family = "tag36h10"
    shape = (6,8)
    filename = "apriltag_target.png"
    size = 50

    tgt = apt.board(shape, family, size)
    imageio.imwrite(filename, tgt)
```

# MIT License

**Copyright (c) 2020 Kevin J. Walchko**

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
