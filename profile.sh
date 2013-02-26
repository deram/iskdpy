#!/bin/sh
export VERSIONER_PYTHON_PREFER_32_BIT=yes
rm profile
python2.7 profile.py
python2.7 stats.py
