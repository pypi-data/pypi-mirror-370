# Chriesibaum's special python utilities



# How to use this module
The usage of the python module is shown in the very basic ./examples/example.py

# Installation

## From PyPI
Download and install the latest package:

```pip3 install cb-pyutils```


## From the sources:

### python the first time

#### Install the python interpreter
On windows download the actual python interpreter from python.org. Do not use the automatic windows installer to install python. On Linux install python with the package manager of your os.

#### Create a virtual python environment
To create the python venv just run:
```. envsetup.sh```



### Build the whl-file
Then finally as soon as you have installed all dependencies, run make build to compile the wheels file and install it with pip.

```make build```

```pip install ./build/mcd_usb_hub_ctrl-<version>-none-any.whl```





