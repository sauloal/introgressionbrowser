#Howto install (with virtualenv) :

git clone ssh://assembly@assembly.ab.wurnet.nl:/home/assembly/tomato150/programs/iBrowser

apt-get install -y build-essential checkinstall libmagickwand-dev openssl sqlite3 libsqlite3-dev libfreetype6{,-dev} zlib1g-dev libjpeg62{,-dev} pkg-config libblas-dev liblapack-dev gfortran
apt-get install -y python-setuptools python-dev python-numpy python-scipy python-matplotlib python-pandas python-sympy python-pip python-imaging

a2enmod wsgi

virtualenv venv && source ./venv/bin/activate

#(takes a while)
pip install --requirement requirements.txt

cd data && scp -c arcfour assembly@assembly:/home/assembly/tomato150/programs/iBrowser/iBrowser.data.tar.gz . && tar xvzf iBrowser.data.tar.gz && rm iBrowser.data.tar.gz && cd - python ibrowser.py

ln -s ibrowser.conf /etc/apache2/mods-available/ibrowser.conf
