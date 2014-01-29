#!/bin/sh
export VERSIONER_PYTHON_PREFER_32_BIT=yes
rm profile

if [ $(uname) == "Darwin" ]
then # osx, 64bit not working
  arch -i386 python2.7 profile.py
  arch -i386 python2.7 stats.py
else
  python2.7 profile.py
  python2.7 stats.py
fi
