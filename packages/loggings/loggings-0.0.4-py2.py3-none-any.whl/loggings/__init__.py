"""
# loggings
Provides more logging tools.

## Usage
```py
>>> import loggings

>>> loggings.warning("hello")
WARNING:root:hello

>>> loggings.get_logger("here", loggings.DEBUG).debug("hello")
DEBUG:here:hello
```

## See Also
### Github repository
* https://github.com/Chitaoji/loggings/

### PyPI project
* https://pypi.org/project/loggings/

## License
This project falls under the BSD 3-Clause License.

"""

from typing import List

from . import core
from .__version__ import __version__
from .core import *

__all__: List[str] = []
__all__.extend(core.__all__)
