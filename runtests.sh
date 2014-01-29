#!/bin/sh

if [ $(uname) == "Darwin" ]
then # osx, 64bit not working
  arch -i386 coverage-2.7 run --branch --source=iskdpy -m unittest discover -v -v -v -s tests -p '*.py'
  coverage-2.7 report
else
  coverage-2.7 run --branch --source=iskdpy -m unittest discover -v -v -v -s tests -p '*.py'
  coverage-2.7 report
fi
