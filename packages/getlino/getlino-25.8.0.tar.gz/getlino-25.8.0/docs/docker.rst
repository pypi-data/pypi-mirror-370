.. _getlino.using_docker:

============================
Using Docker to test getlino
============================

Testing getlino is quite different from testing Lino itself in that getlino is a
tool that modifies the system configuration of a Linux machine.  You obviously
don't want it to do this on the computer you are using for development.

.. highlight:: console

Quick introduction to Docker
============================

A Docker **container** is like a virtual machine, but it stores only the things
that you changed after installing the **image**. A Docker **image** contains a
whole operating system:.

Running :cmd:`inv prep` in the getlino repository will build a set of Docker
images needed for running the getlino test suite.  You don't need to run it
before every test run, only once after each modification in the getlino source
code.

- ``debian_updated`` = a virgin Debian buster + apt upgrade + create a user "lino"
- ``debian_with_getlino`` = `debian_updated` + add the current getlino source files
- ``ubuntu_updated`` : same as `debian_updated` but with Ubuntu
- ``ubuntu_with_getlino`` : same as `debian_with_getlino` but with Ubuntu

You can see the available docker images on your computer::

  $ docker image ls
  REPOSITORY            TAG                 IMAGE ID            CREATED             SIZE
  ubuntu_with_getlino   latest              509d56b09981        3 hours ago         513MB
  debian_with_getlino   latest              a96d832cb84c        3 hours ago         598MB
  ubuntu_updated        latest              4171a574c2d7        4 days ago          513MB
  debian_updated        latest              f29ed368ec5d        4 days ago          598MB
  ubuntu                bionic              d27b9ffc5667        2 weeks ago         64.2MB
  debian                buster              1b686a95ddbf        6 weeks ago         114MB


You can run an interactive session in a docker container using one of those
images::

  $ docker run -it debian_with_getlino /bin/bash
  lino@97621d803236:/src$

.. We give it an explicit name (`--name mytest`) because that's easier to remember
  than the automatically generated names given by Docker.

The effect of this is that you are now inside a bash session on your container.
Feel free to play around::


  lino@97621d803236:/src$ pwd
  /src
  lino@97621d803236:/src$ ls -al
  total 16
  drwxr-xr-x 1 lino lino 4096 Jul 27 09:50 .
  drwxr-xr-x 1 root root 4096 Jul 27 11:24 ..
  drwxr-xr-x 4 root root 4096 Jul 27 09:50 getlino
  -rw-rw-r-- 1 root root  260 Jul 10 10:02 setup.py
  lino@97621d803236:/src$ echo "Hello, world!" > hello.txt

Now hit :kbd:`Ctrl-D` to terminate your bash session.  This will put your
container into the state "exited".  You can see the status of all your
containers by saying::

  $ docker ps -a
  CONTAINER ID        IMAGE                 COMMAND             CREATED              STATUS                     PORTS               NAMES
  97621d803236        debian_with_getlino   "/bin/bash"         About a minute ago   Exited (0) 5 seconds ago                       sharp_austin

Copy the name of your container (`97621d803236` in this example, but yours is
likely to be different) to your clipboard. Now let's say you want to continue
working on this container:

.. code-block::

  $ docker start -i 97621d803236
  lino@97621d803236:/src$ cat hello.txt
  Hello, world!
  lino@97621d803236:/src$  # hit [Ctrl-D] to exit

As you can see, the :file:`hello.txt` from your previous session is still there.

You can start a container in "detached mode", that is, without attaching it to
your terminal. The :cmd:`docker start` command returns you immediately to the
shell prompt and the container continues running in background::

  $ docker start 97621d803236

You can now run one bash command at a time from the command line::

  $ docker exec 97621d803236 /bin/bash -c "cat hello.txt"
  Hello, world!
  $

We can verify that the container is still running in the background::

  $ docker ps -a
  CONTAINER ID  IMAGE                COMMAND       CREATED       STATUS          PORTS  NAMES
  97621d803236  debian_with_getlino  "/bin/bash"   2 hours ago   Up 10 seconds          sharp_austin

Let's tidy up and remove our container::

  $ docker container rm 97621d803236
  Error response from daemon: You cannot remove a running container
  97621d803236e46b66917aae8bc6fb01ea3ab3f8749e374d33a818516c833509.
  Stop the container before attempting removal or force remove

Yes, we started the container in detached mode, it would run forever if we don't
stop it::

  $ docker container stop 97621d803236
  97621d803236

Now we can remove it::

  $ docker container rm 97621d803236

What we saw here is basically all we do in our test suite.  Let's have a look at
the file :file:`tests/test_docker.py`

..

  $ docker run --publish 8000:8080 --detach --name mycont getlino_debian

Docker uses much disk space
===========================

How to see how much disk space docker is using on your computer::

  $ docker system df
  TYPE                TOTAL               ACTIVE              SIZE                RECLAIMABLE
  Images              34                  5                   5.1GB               5.1GB (99%)
  Containers          11                  2                   17GB                14.13GB (83%)
  Local Volumes       0                   0                   0B                  0B
  Build Cache         0                   0                   0B                  0B

To get more details, you can also run::

  $ docker system df -v

From time to time I tidy up and remove all rebuildable containers::

  $ docker system prune
  WARNING! This will remove:
    - all stopped containers
    - all networks not used by at least one container
    - all dangling images
    - all dangling build cache

  Are you sure you want to continue? [y/N] y
  Deleted Containers:
  cdd408dc0ee130d4498c82f0eed6609445b3ae290ef21c7739ef29ceca99fbd4
  493ae1128f25bc144598661eaf854de527cdc7b4795ba1a34f9e46a0aa852012
  48f9d5220778b8efd7db4bb041659b9b058f993e234e770e803e4cbeb18e4124
  ...
  Total reclaimed space: 27.53GB

If you want it to prune also the volumes, not only the images::  

  $ docker system prune --volumes


Sources consulted:

- https://docker-curriculum.com/
- https://stackoverflow.com/questions/21928691/how-to-continue-a-docker-container-which-has-exited
