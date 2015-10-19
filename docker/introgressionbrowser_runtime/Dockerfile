#docker build --rm -t sauloal/introgressionbrowser_runtime .

FROM ubuntu:14.04.3

ENV DEBIAN_FRONTEND noninteractive

RUN bash -c "echo -e 'deb mirror://mirrors.ubuntu.com/mirrors.txt trusty main restricted universe multiverse\ndeb mirror://mirrors.ubuntu.com/mirrors.txt trusty-updates main restricted universe multiverse\ndeb mirror://mirrors.ubuntu.com/mirrors.txt trusty-backports main restricted universe multiverse\ndeb mirror://mirrors.ubuntu.com/mirrors.txt trusty-security main restricted universe multiverse' > /etc/apt/sources.list" && \
    apt-get clean all  && \
    apt-get update     && \
    apt-get -y upgrade && \
    apt-get install -y -f libapache2-mod-wsgi apache2 nano build-essential            \
            checkinstall openssl sqlite3 libsqlite3-dev git nano                      \
            libfreetype6 libfreetype6-dev zlib1g-dev libjpeg62 libjpeg62-dev          \
            pkg-config libblas-dev liblapack-dev gfortran zlib1g-dev               && \
    apt-get install -y -f python-setuptools python-dev python-numpy python-scipy      \
            python-matplotlib python-pandas python-sympy python-pip python-imaging    \
            python-numpy pylint                                                    && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*                 && \
    a2enmod wsgi && a2enmod proxy && a2enmod proxy_http && a2enmod rewrite         && \
    mkdir -p /etc/apache2/mods-available/

ADD requirements.txt /requirements.txt

RUN pip install --requirement /requirements.txt

