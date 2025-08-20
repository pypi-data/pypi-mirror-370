#!/bin/bash
# Providing a Lino server <https://hosting.lino-framework.org/root/>
# this is designed to run as root
set -xe
set

DBENGINE=$1
WEBSERVER_NAME=$2
echo "DBENGINE is $DBENGINE"
echo "WEBSERVER_NAME is $WEBSERVER_NAME"
cat /etc/debian_version

# Preparing a new server¶
uname -a
df -h
# free -h

apt-get update
apt-get -y upgrade
# avoid warning: setlocale: LC_ALL: cannot change locale (en_US.UTF-8)
apt-get install -y tzdata locales-all

# Install sudo package and disable password prompt for sudoers
apt-get install sudo
echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Creating a user account¶
adduser --disabled-password --gecos '' lino
adduser lino sudo
adduser lino www-data

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
# tested_applications="cosi avanti noi amici tera voga shop welcht"
tested_applications="cosi avanti noi amici"

# create /src directory and copy required project source files to the image

# mkdir /src
# chown lino:lino -R /src
# RUN echo 1; pwd ; ls -l

apt-get install -y pip virtualenv git redis-server pkg-config
# sudo apt-get install -y python3-venv git

# start redis server
service redis-server start


# https://hosting.lino-framework.org/install/#set-up-a-master-environment
# create and activate a master virtualenv
mkdir -p /usr/local/lino/shared/env
cd /usr/local/lino/shared/env
chown root:www-data .
chmod g+ws .
virtualenv master

.  master/bin/activate
# update pip to avoid warnings
pip3 install -U pip

# install getlino (the dev version)
cd $CI_PROJECT_DIR

pip3 install -e .

# apt search mysql
if [ "$WEBSERVER_NAME" = apache ] ; then
    apt search apache
    apt search http
    apt search httpd
    apt search mod-wsgi
fi
apt search apache
# sudo apt-get install -y redis redis-server redis-tools # getlino installs it already
# ls /usr/sbin | grep service # We have service installed

DB_ARGS=""
_DB_NAME=""

# dump environment variables
#env

if [ "$DBENGINE" = mysql ] ; then
  sudo apt-get install -y default-libmysqlclient-dev
  # DB_ARGS="--db-host $MYSQL_HOST"  # --db-port 3306 --db-user $MYSQL_USER --db-password $MYSQL_PASSWORD"
  # _DB_NAME=$MYSQL_DATABASE
# Create PostgreSQL user if needed
elif [ "$DBENGINE" = postgresql ]; then
  sudo apt install -y postgresql postgresql-client libpq-dev
  sudo adduser --system --group --home /var/lib/postgresql postgres
  sudo service postgresql restart

  POSTGRES_USER=${POSTGRES_USER:-lino_user}
  POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-GvkadwjTc-k}

  echo "Creating PostgreSQL user: $POSTGRES_USER"
     if id "postgres" &>/dev/null; then
         sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname = '$POSTGRES_USER'" | grep -q 1 || \
         sudo -u postgres psql -c "CREATE USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';"
     else
         echo "PostgreSQL system user 'postgres' not found. Skipping user creation."
     fi
  DB_ARGS="--db-host postgres --db-user $POSTGRES_USER --db-password $POSTGRES_PASSWORD --db-engine $DBENGINE"
  DB_NAME=$POSTGRES_DB
fi

#elif [ "$DBENGINE" = postgresql ] ; then
#  sudo apt-get install -y libpq-dev
#  DB_ARGS="--db-host postgres --db-user $POSTGRES_USER --db-password $POSTGRES_PASSWORD --db-engine $DBENGINE"
#  _DB_NAME=$POSTGRES_DB
#fi

if [ "$3" = 1 ] ; then
    export GITLAB_CI=1
    export GITLAB_CI_DB_NAME=$_DB_NAME
fi

getlino configure --batch --monit --no-clone --appy --web-server $WEBSERVER_NAME --db-engine $DBENGINE

ls -al /etc/getlino/lino_bash_aliases
. /etc/getlino/lino_bash_aliases

SUFFIX=1

if [ -n "$4" ] ; then
    # runs from lino_app|$4/.gitlab-ci.yml
    # run with latest lino, xl; pypi releases are tested from getlino/.gitlab-ci.yml
    cd $CI_PROJECT_DIR
    cd ..
    # remove existing packages
    if [ -n "$(ls | grep '^lino$')" ] ; then
        rm -r lino
    fi
    if [ -n "$(ls | grep '^xl$')" ] ; then
        rm -r xl
    fi
    git clone https://gitlab.com/lino-framework/lino.git
    git clone https://gitlab.com/lino-framework/xl.git
    cd lino
    pip3 install -e .
    cd ../xl
    pip3 install -e .

    getlino startsite --batch $DB_ARGS $4 "$4$SUFFIX"
else
    echo $tested_applications
    for APP in $tested_applications ; do
        getlino startsite --batch $DB_ARGS $APP "$APP$SUFFIX"
    done
fi
