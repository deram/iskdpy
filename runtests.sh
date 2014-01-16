#!/bin/sh
arch -i386 python2.7 -m unittest discover -s tests -p '*.py' -v
