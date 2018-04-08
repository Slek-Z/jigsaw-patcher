# jigsaw-patcher #

xdelta3 gui in pyGTK able to create a zip with the xdelta3 binary and the executable script (.bat and/or .sh)

## Linux ##

The programs and dependencies are **python 2.6**, **gtk2**, **pygtk**, **pygobject** and **pycairo**

Any modern distro would bring it by default, otherwise just google for a howto pygtk in 0, seconds for your distro. You will probably need root access.

A shell script is also available to interface `xdelta3`. To generate the *.zip* patch, just run:
```
./jigsaw-patcher.sh SOURCE TARGET
```

## Windows ##

You need some dependencies to be able to run the application. For a detailed explanation follow this [link](http://www.pygtk.org/downloads.html).

The programs and dependencies are **python 2.6**, **gtk2**, **pygtk**, **pygobject** and **pycairo**. Some useful links:
  * [ActivePython](http://www.activestate.com/activepython/downloads)
  * [GTK2](http://gtk-win.sourceforge.net/home/index.php/Main/Downloads)
  * [PyGTK](http://ftp.gnome.org/pub/GNOME/binaries/win32/pygtk/)
  * [PyCairo](http://ftp.gnome.org/pub/GNOME/binaries/win32/pycairo/)
  * [PyGobject](http://ftp.gnome.org/pub/GNOME/binaries/win32/pygobject/)