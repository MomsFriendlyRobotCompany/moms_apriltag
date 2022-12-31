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

See the jupyter notebook in `example/examples.ipynb` for how to use this.

This package create a simple numpy image that can then be saved
to a PNG or JPEG image and printed. For circular or custom tags,
there is a `toRGBA()` function to save the tag to a `png` using
any image library that can accept `numpy` array images.

Supported families are shown in the table below:

| Family    | Generation | Hamming | Size | Data Bits | Unique Tags |
|-----------|------------|---------|------|-----------|-------------|
| `tag16h5` | 2          | 5       | 4x4  | 16        | 30
| `tag25h9` | 2          | 9       | 5x5  | 25        | 35
| `tag36h10`| 2          | 10      | 5x5  | 36        | 2,320
| `tag36h11`| 2          | 11      | 5x5  | 36        | 587
| `tagCircle21h7`| 3     | 7       | 9x9  | 36        | 38
| `tagCircle49h12`| 3    | 12      | 11x11| 49        | 65,535
| `tagCustom48h12`| 3    | 12      | 10x10| 48        | 42,211
| `tagStandard41h12`| 3  | 12      | 9x9  | 41        | 2,115
| `tagStandard52h13`| 3  | 13      | 10x10| 52        | 48,714

[ref](https://optitag.io/blogs/news/designing-your-perfect-apriltag)

```python
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

```python
# for AprilTag v2
from moms_apriltag import TagGenerator2
from matplotlib import pyplot as plt

tg = TagGenerator2("tag16h5")
tag = tg.generate(4)

plt.imshow(tag, cmap="gray)
```

```python
# for AprilTag v3
from moms_apriltag import TagGenerator3
from matplotlib import pyplot as plt

tg = TagGenerator3("tagStandard41h12")
tag = tg.generate(137)

plt.imshow(tag, cmap="gray)
```

## Decoders

- pupil labs (tested): https://github.com/pupil-labs/apriltags can decode gen 2 and 3 tags
- `cv2.aruco` (tested): can decode gen 2 tags only
- WillB97: https://github.com/WillB97/pyapriltags can decode gen 2 and 3 tags

# Todo

- [ ] refactor board code
- [ ] enable apriltag v3 markers in board

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
