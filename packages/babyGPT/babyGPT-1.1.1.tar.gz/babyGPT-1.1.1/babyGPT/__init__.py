#!/usr/bin/env python

import sys

if sys.version_info[0] == 3:
    from babyGPT.babyGPT import __version__
    from babyGPT.babyGPT import __author__
    from babyGPT.babyGPT import __date__
    from babyGPT.babyGPT import __url__
    from babyGPT.babyGPT import __copyright__
    from babyGPT.babyGPT import babyGPT
else:
    sys.exit("Aborted  ---  babyGPT can only be run with Python3")






