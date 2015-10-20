#docker run -it --rm
# -v $PWD/data:/var/www/ibrowser/data 
# -v $PWD/access.log:/var/log/apache2/access.log 
# -v $PWD/error.log:/var/log/apache2/error.log 
# sauloal/introgressionbrowser
#
#--security-context apparmor:unconfine 
# --security-context 
#
#docker build --rm -t sauloal/introgressionbrowser .

FROM sauloal/introgressionbrowser_runtime

RUN cd /var/www && git clone https://github.com/sauloal/introgressionbrowser.git ibrowser

WORKDIR /var/www/ibrowser

VOLUME /var/www/ibrowser/data
VOLUME /var/log/apache2/access.log
VOLUME /var/log/apache2/error.log

CMD /var/www/ibrowser/reloader.py /var/www/ibrowser/ibrowser.py /var/www/ibrowser/data
