#!/bin/bash
# This script *should* be doing what is instructed in
# "Install a Lino developer environment"
# <https://dev.lino-framework.org/dev/install>
set -xe
set
shopt -s expand_aliases

DBENGINE=$1
WEBSERVER_NAME=$2
echo "DBENGINE is $DBENGINE"
echo "WEBSERVER_NAME is $WEBSERVER_NAME"
cat /etc/debian_version

# Preparing a new server¶
uname -a
df -h
# free -h

apt -y update
apt -y upgrade
# avoid warning: setlocale: LC_ALL: cannot change locale (en_US.UTF-8)
apt-get install -y tzdata locales-all

# Avoid getting "The virtual environment was not created successfully because
# ensurepip is not available.":
apt-get install -y python3-venv

# Install sudo package and disable password prompt for sudoers
apt-get install -y sudo supervisor
echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Creating a user account¶
adduser --disabled-password --gecos '' joe
adduser joe sudo
adduser joe www-data

pwd
cat /etc/debian_version


# https://hosting.lino-framework.org/install/

# create /src directory and copy required project source files to the image
#sudo  mkdir /src
#sudo chown lino:lino -R /src


# TERM=linux
# PYTHONUNBUFFERED=1
# LC_ALL=en_US.UTF-8
# LANG=en_US.UTF-8
# TZ=Europe/Brussels
tested_applications="cosi avanti noi amici tera voga shop welcht"

# create /src directory and copy required project source files to the image

# mkdir /src
# chown lino:lino -R /src
# RUN echo 1; pwd ; ls -l

#### apt-get install -y python3-venv
# before: pip virtualenv
# sudo apt-get install -y python3-venv


# https://hosting.lino-framework.org/install/#set-up-a-master-environment
# create and activate a master virtualenv
cd   # go to your home directory
mkdir lino
python3 -m venv lino/env
. lino/env/bin/activate

cat .bashrc
echo "" >> .bashrc
echo ". lino/env/bin/activate" >> .bashrc

# update pip to avoid warnings
pip install -U pip setuptools

# Make sure that your default environment is correctly set:
which python

# install getlino (the dev version)
cd $CI_PROJECT_DIR
pip install -e .

getlino configure --clone --devtools --batch --appy --redis

# libreoffice is needed for inv prep, let's verify whether it was installed:
cat /etc/supervisor/conf.d/libreoffice.conf
tail -n 50 /var/log/supervisor/supervisord.log
service supervisor status

# ls -al ~/.lino_bash_aliases
# . ~/.lino_bash_aliases
ls -al /etc/getlino/lino_bash_aliases
cat /etc/getlino/lino_bash_aliases
. /etc/getlino/lino_bash_aliases

# https://dev.lino-framework.org/dev/install/index.html

pp -l

go polly
pm prep -b

# we can't test runserver in batch mode

go book
inv install --batch  # not needed on a real install but might be needed here
inv prep


# https://dev.lino-framework.org/dev/hello/index.html
getlino startsite polly first --batch

# test the go alias:
go first
cat manage.py

# test the atelier config example shown on
# https://dev.lino-framework.org/dev/env.html#configuring-atelier
go book
python docs/dev/atelier_config_example.py

echo $VIRTUAL_ENV
pip freeze
