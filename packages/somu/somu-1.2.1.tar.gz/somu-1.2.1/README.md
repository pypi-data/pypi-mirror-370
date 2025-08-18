# self-organizing-map
A high-performance implementation of the Self-Organizing Map (SOM) algorithm in Rust, exposed as a Python module. 

![image](https://raw.githubusercontent.com/ventus550/somu/refs/heads/master/demos/sphere.png)

# Installtion
This module interfaces with the [ArrayFire](https://arrayfire.org/docs/installing.htm#gsc.tab=0) library (version 3.8.0).
To ensure proper functionality, make sure the ArrayFire shared libraries are discoverable by the system. You can do this by updating your LD_LIBRARY_PATH environment variable:
```
export LD_LIBRARY_PATH=/path/to/arrayfire/lib64:$LD_LIBRARY_PATH
```

Then to install the latest version of the package from PyPI, simply run:
```
pip install somu
```

# Usage
```python
from somu import som
from numpy import random

data = random.rand(1000, 2)
som(data, (10, 10))
```

# Demo requirements
Before running the demos make sure to have the required packages installed:
```
pip install -r demos/requirements.txt
```

Shield: [![CC BY-NC 4.0][cc-by-nc-shield]][cc-by-nc]

This work is licensed under a
[Creative Commons Attribution-NonCommercial 4.0 International License][cc-by-nc].

[![CC BY-NC 4.0][cc-by-nc-image]][cc-by-nc]

[cc-by-nc]: https://creativecommons.org/licenses/by-nc/4.0/
[cc-by-nc-image]: https://licensebuttons.net/l/by-nc/4.0/88x31.png
[cc-by-nc-shield]: https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg
