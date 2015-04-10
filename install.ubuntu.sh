apt-get install -y build-essential checkinstall libmagickwand-dev openssl sqlite3 libsqlite3-dev libfreetype6{,-dev} zlib1g-dev libjpeg62{,-dev} pkg-config libblas-dev liblapack-dev gfortran
apt-get install -y python-setuptools python-dev python-numpy python-scipy python-matplotlib python-pandas python-sympy python-pip python-imaging

a2enmod wsgi

pip install --user --upgrade --requirement requirements.txt

ln -s ibrowser.conf /etc/apache2/mods-available/ibrowser.conf
