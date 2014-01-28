#!/bin/sh
arch -i386 coverage-2.7 run --branch --source=iskdpy -m unittest discover -v -v -v -s tests -p '*.py'
coverage report
