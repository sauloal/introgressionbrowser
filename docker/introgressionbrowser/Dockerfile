#docker run -it --security-context -v $PWD:/var/www/ibrowser -v $PWD/data:/var/www/ibrowser/data -v $PWD/access.log:/var/log/apache2/access.log -v $PWD/error.log:/var/log/apache2/error.log sauloal/introgressionbrowser
#--security-context apparmor:unconfine 
#docker build --rm -t sauloal/introgressionbrowser .

FROM sauloal/introgressionbrowser_runtime

RUN cd /var/www && git clone https://github.com/sauloal/introgressionbrowser.git ibrowser

WORKDIR /var/www/ibrowser

