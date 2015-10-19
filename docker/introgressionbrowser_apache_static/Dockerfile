#docker run -it --security-context -v $PWD:/var/www/ibrowser -v $PWD/data:/var/www/ibrowser/data -v $PWD/access.log:/var/log/apache2/access.log -v $PWD/error.log:/var/log/apache2/error.log sauloal/introgressionbrowser
#--security-context apparmor:unconfine 
#docker build --rm -t sauloal/introgressionbrowser_apache_static .

FROM sauloal/introgressionbrowser_runtime

ENV DEBIAN_FRONTEND noninteractive

RUN mkdir -p /etc/apache2/mods-available/ && \
    mkdir -p /var/www/ibrowser            && \
    ln -s /var/www/ibrowser/static/       /var/www/html/static

#    sed -ie "s/Listen 80/Listen 8000/" /etc/apache2/ports.conf                     && \

ADD ibrowser.conf /etc/apache2/mods-enabled/ibrowser.conf

WORKDIR /var/www/ibrowser

VOLUME [ "/var/www/ibrowser"      ]
VOLUME [ "/var/www/ibrowser/data" ]
