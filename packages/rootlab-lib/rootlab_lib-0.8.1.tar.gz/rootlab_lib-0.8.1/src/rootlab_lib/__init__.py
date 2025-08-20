"""
## What is this?
A library of data analysis tools for the RootLab at CWRU. This library contains functions commonly used for data analysis in the lab. For obvious reasons, data used for the modules tests is not be shared.

## Instructions
### Pip
With basic pip, use:
```
pip install rootlab-lib
```

## Documentation
`pdoc` is used to generate all of the documentation for this library. You can access it locally by opening `index.html` in the `doc` folder. If you need help with a function, it is probably over-documented in the library documentation.

## Updating
If you have permission and a valid key, you can update the package using the update.bat script. This will attempt to push to PyPI, and will prompt for a API token at the end of the script running. This will regenerate documentation. Ensure that you are working with a valid version of the necessary packages, and that the version of the library you are trying to push has not been used already. If either of these are not satisfied, the tool will tell you what went wrong and it is then your job to fix it.

### Spyder
If using Spyder (Conda is your package manager or you do not have pip), you MUST download python [here](https://www.python.org/downloads/) and change the interpreter for Spyder to the downloaded python version. When you download python using the link above, note the installation folder of the interpreter and copy it to your clipboard so that you can paste the path in Spyder. To change the path to the interpreter in Spyder, Select `Tools`, `Settings`, then `Python Interpreter`. At the top of this page, check the box that allows you to enter a custom interpreter, paste the path you copied earlier. Restart Spyder, and enter the command it tells you to use to fix any issues with the new interpreter. It should be something like `pip install spyder-kernels`. You can now run `pip install rootlab-lib` without issue. You may need to restart Spyder again for the changes to take effect.

If you already have python installed, then you must find out where your python interpreter is located on your system. This can be down by opening a terminal and typing `where python`. You can also just google it if this doesn't work!
"""

from .serial_reader import *
from .voltage_analysis import *
from .plateau_processing import *
from .source_meter_analysis import *
from .vkx150_analysis import *
from .multilayer_reader import *
from .instron_analysis import *
from .mark10_analysis import *
from .arduino import *
