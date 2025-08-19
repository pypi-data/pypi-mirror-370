#!/usr/bin/env bash

set -e

apt-get update -y
apt-get install -y bsdmainutils

pip install wheel build
python -m build

# do a test install from both source and wheel
sdist=`find dist -maxdepth 1 -name *.tar.gz`
wheel=`find dist -maxdepth 1 -name *.whl`

for target in $sdist $wheel; do
    python -m venv test.venv
    . test.venv/bin/activate
    pip install --upgrade pip setuptools
    pip install $target
    rm -r test.venv
done
