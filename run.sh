#!/bin/sh
if [ $(uname) == "Darwin" ]
then # osx, 64bit not working
  arch -i386 python2.7 iskdpy.py
else
  python2.7 iskdpy.py
fi
