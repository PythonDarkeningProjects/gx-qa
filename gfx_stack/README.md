# Graphic Stack for linux


## What is it?

The Graphic Stack is a set of drivers for a specific purpose, the script that build the drivers is : gfxStack.py.


## Prerequisites

This script depends of several libraries, most of them can be installed with [tux.sh](https://github.intel.com/linuxgraphics/gfx-qa-tools/blob/master/tux.sh)

```
$ tux.sh

Select option 2 "Utilities"
Select option 8 "Install all the dependencies needed for gfx stack"
```
Note : if some dependency is missing (you will notice when start to build the graphic drivers), please notify to

humberto.i.perez.rodriguez@intel.com

or submit a patch to this [repository](https://github.intel.com/linuxgraphics/gfx-qa-tools)

I highly recommend Ubuntu 16.10 for build the Graphic Stack with this script in order to avoid issues with several dependencies.


## How to use it?

gfxStack.py script needs of a config.yml file properly configurated.

## How to create/configurate a config.yml?

* xserver-xorg - in order to build the whole xserver-xorg you can use the following script :

[xorg_config.py](https://github.intel.com/linuxgraphics/gfx-qa-tools/blob/master/gfx_stack/xorg_config.py)

```
$ python xorg_config.py
```

This script will generated a config.yml with all the keys/values that gfxStack.py needs, e.g :

```
2D_Driver:
  glamour: true
  sna: false
dut_config:
  dut_user: gfx
latest_commits:
  value: false
miscellaneous:
  mailing_list:
  - humberto.i.perez.rodriguez@intel.com
  maximum_permitted_time: 10000
  server_for_upload_package: linuxgraphics.intel.com
  server_user: gfxserver
  upload_package: true
patchwork:
  cairo:
    apply: false
    path: ''
  checkBeforeBuild: true
specific_commit:
  cairo: 99427c3f4f6ce7ce3c95c4caa4d2b8ff7c0093d9
```

As a comment this config.yml also includes the drivers for intel-gpu-tools, the main difference is that the build of this drivers can take a while compared with the following package.


* intel-gpu-tools - in order to build all the necessary drivers you need to take the following config.yml and put it in the same folder where gfxStack.py resides.


[config.yml](https://github.intel.com/linuxgraphics/gfx-qa-tools/blob/master/gfx_stack/config.d/intel-gpu-tools/config.yml)

### Optional step

If you want a email notification once the script finished of build the drivers add your email in :


```
mailing_list --> put your email if you want to receive an email when your debian package is ready

```

## Starting to build the Graphic Stack

Once you have your config.yml as you want, simply run the following command :

```
$ python gfxStack.py
```