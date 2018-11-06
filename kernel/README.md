# INTEL® Linux Graphics QA

## Getting Started

### Description

- kernel_build.py is a script designed to build kernels from drm-tip.

[drm-tip](https://cgit.freedesktop.org/drm-tip)

if --tag option is passed as argument, a new tag for drm-intel-qa will be generated (if any)
in the following url:

- [QA-tag in bifrost.intel.com](http://bifrost.intel.com/gitlist/drm-tip)


### How this works for drm-intel-qa

1. (if any) “UTC integration manifest” legend is on drm-tip, take it
2. Else take HEAD

Job should run on Monday at 9 AM (GDC side) because Daniel Vetter push his
integration manifest earlier in the morning.
Your job should also give you the ability to create a tag manually on demand.

Tag format is: drm-intel-qa-testing-YYY-MM-DD
(e.g: drm-intel-qa-testing-2016-10-18)


### How this works for drm-tip

1. Always take HEAD in order to build it.


### Differences between drm-tip and drm-intel-qa

The only difference is that the commits built for drm-intel-qa will have a tag in our system in order to preserve them
and avoid the rebase from [drm-tip](https://cgit.freedesktop.org/drm-tip).


### Ways to update drm-intel
1. git pull origin drm-tip

#### Command description

This command will brought all the new commits from [drm-tip](https://cgit.freedesktop.org/drm-tip)
usually this command will have conflicts to merge the current kernel source code changes
with the ones in upstream, for fix this we have to do the following command.

2. git reset --hard origin/drm-tip

#### Command description

This command will deleted the current changes in your kernel source code in order to merge the changes
downloaded by the command above and then it will point to the newer commit downloaded.


### References
- [drm-intel patch and upstream merge flow and time line explained](https://01.org/linuxgraphics/gfx-docs/maintainer-tools/drm-intel.html)
