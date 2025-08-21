# A lightwight python control module for MCD USB Hubs

"USB Hub 2.0 6-Port, Switchable"


![image](doc/hub.png)



This python module controls the switches of usb hub. This very first release supports only a basic functionality such as enable and disable a port. The control interface would support much more functionality.

For more details on the hub see:
https://www.mcd-elektronik.com/products/conline-control-systems/usb-hub-20-6-port-switchable.html


# How to use this module
The usage of the python module is shown in the very basic ./examples/example.py

# Installation

## From PyPI
Download and install the latest package:

```pip3 install mcd_usb_hub_ctrl```


## From the sources:

### python the first time

#### Install the python interpreter
On windows download the actual python interpreter from python.org. Do not use the automatic windows installer to install python. On Linux install python with the package manager of your os.

#### Create a virtual python environment
This has only to be done once to create the virtual environment

```python3 -m venv .venv```

#### Init the python virtual environment
This is needed every time you open the shell

##### On linux systems

```source .venv/bin/activate```

##### On windows systems

```.venv\Scripts\activate```


#### Get the required packages to be up and running
This has only to be done once to use the lib

```pip install -r requirements.txt```

And for dev purposes some additional packages:

```pip install -r requirements_dev.txt```



### Build the whl-file
Then finally as soon as you have installed all dependencies, run make build to compile the wheels file and install it with pip.

```make build```

```pip install ./build/mcd_usb_hub_ctrl-<version>-none-any.whl```





