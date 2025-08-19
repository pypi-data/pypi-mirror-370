#!/usr/bin/env bash

set -e

apt-get update -y                           || yum -y check-update                     || true;
apt-get install -y openssh-client rsync git || yum install -y openssh-client rsync git || true;

pip install setuptools wheel twine
twine upload dist/*
