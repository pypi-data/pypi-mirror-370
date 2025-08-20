set -e  # exit on error

# We locally cache a debian/ubuntu with the latest updates so that we don't need
# to hit their servers each time we run "inv prep test". From time to time it
# might be usefule to run refresh our cache:
#
# stop and delete all containers
# docker container prune
# docker system prune

# docker build -t debian_updated -f Dockerfiles/debian_updated .
# docker build -t ubuntu_updated -f Dockerfiles/ubuntu_updated .
# docker build -t debian_with_getlino -f Dockerfiles/debian_with_getlino .
# docker build -t ubuntu_with_getlino -f Dockerfiles/ubuntu_with_getlino .

# docker build -t getlino_ubuntu -f Dockerfiles/ubuntu .
# docker build --no-cache -t getlino_debian -f Dockerfiles/debian .
# docker build --no-cache -t getlino_ubuntu -f Dockerfiles/ubuntu .
