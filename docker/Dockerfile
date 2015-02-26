#docker run -it --security-context -v $PWD:/var/www/ibrowser -v $PWD/data:/var/www/ibrowser/data -v $PWD/access.log:/var/log/apache2/access.log -v $PWD/error.log:/var/log/apache2/error.log sauloal/introgressionbrowser
#--security-context apparmor:unconfine 
#docker build --rm -t sauloal/introgressionbrowser .

FROM ubuntu:14.10

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get clean all && apt-get update && apt-get -y upgrade                      && \
    apt-get install -y -f libapache2-mod-wsgi apache2 nano build-essential            \
            checkinstall openssl sqlite3 libsqlite3-dev                               \
            libfreetype6 libfreetype6-dev zlib1g-dev libjpeg62 libjpeg62-dev          \
            pkg-config libblas-dev liblapack-dev gfortran zlib1g-dev               && \
    apt-get install -y -f python-setuptools python-dev python-numpy python-scipy      \
            python-matplotlib python-pandas python-sympy python-pip python-imaging    \
            python-numpy pylint                                                    && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

#libmagickwand-dev
#libmagickcore-dev
#libjpeg62 libjpeg62-dev 
#libfreetype6 libfreetype6-dev 

RUN a2enmod wsgi && a2enmod proxy && a2enmod proxy_http && a2enmod rewrite         && \
    sed -ie "s/Listen 80/Listen 8000/" /etc/apache2/ports.conf                     && \
    mkdir -p /etc/apache2/mods-available/ && mkdir -p /var/www/ibrowser            && \
    ln -s /var/www/ibrowser/static/       /var/www/html/static

ADD requirements.txt /requirements.txt

RUN pip install --requirement /requirements.txt

ADD ibrowser.conf /etc/apache2/mods-enabled/ibrowser.conf

WORKDIR /var/www/ibrowser

VOLUME [ "/var/www/ibrowser"      ]
VOLUME [ "/var/www/ibrowser/data" ]
