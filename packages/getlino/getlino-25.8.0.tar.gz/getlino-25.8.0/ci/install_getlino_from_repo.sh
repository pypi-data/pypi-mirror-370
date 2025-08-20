#!/bin/bash
set -e
uname -a
apt-get update
apt-get -y upgrade
apt-get install -y tzdata locales-all python3 python3-dev python3-setuptools python3-pip apt-utils build-essential sudo
export LC_CTYPE=en_US.UTF-8
export LC_ALL=en_US.UTF-8
python -V  # Print out python version for debugging
pip install virtualenv
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
pip install -e .
