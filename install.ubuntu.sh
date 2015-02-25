apt-get install -y python-setuptools build-essential libfreetype6 libfreetype6-dev zlib1g-dev libjpeg62 libjpeg62-dev python-pip python-dev python-numpy python-scipy python-matplotlib python-imaging pkg-config libblas-dev liblapack-dev gfortran apache2

a2enmod wsgi

easy_install --user flask
easy_install --user ete2
easy_install --user PIL
easy_install --user Image
easy_install --user sqlalchemy
easy_install --user pysha3
easy_install --user rsa

ln -s ibrowser.conf /etc/apache2/mods-available/ibrowser.conf
