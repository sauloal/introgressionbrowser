#docker run -it --security-context apparmor:unconfine -v $PWD/data:/var/www/ibrowser/data -v $PWD/access.log:/var/log/apache2/access.log -v $PWD/error.log:/var/log/apache2/error.log ibrowser
#docker build -t ibrowser .

FROM ubuntu:14.10

RUN apt-get clean all && \
    apt-get update && \
    apt-get install -y libapache2-mod-wsgi apache2 nano && \
    a2enmod wsgi && a2enmod proxy && a2enmod proxy_http && a2enmod rewrite && \
    sed -ie "s/Listen 80/Listen 8000/" /etc/apache2/ports.conf 

RUN apt-get install -y python-virtualenv libjpeg62 libjpeg62-dev libfreetype6 libfreetype6-dev \
    zlib1g-dev python-setuptools build-essential zlib1g-dev libjpeg62 libjpeg62-dev \
    python-pip python-dev python-numpy python-scipy python-matplotlib \
    python-imaging pkg-config libblas-dev liblapack-dev gfortran && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ADD iBrowser         /var/www/ibrowser

WORKDIR /var/www/ibrowser

#ln -s /var/www/ibrowser/static/       /var/www/html/static && \
RUN ln -s /var/www/ibrowser/ibrowser.conf /etc/apache2/mods-enabled/ibrowser.conf && \
    virtualenv venv && \
    bash -c "source ./venv/bin/activate && \
    pip install --requirement /var/www/ibrowser/requirements.txt"

VOLUME [ "/var/www/ibrowser/data" ]
