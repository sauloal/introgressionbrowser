Howto install (with virtualenv) :

git clone ssh://assembly@assembly.ab.wurnet.nl:/home/assembly/tomato150/programs/iBrowser

apt-get install python-virtualenv libjpeg62{,-dev} libfreetype6 libfreetype6{,-dev} zlib1g-dev python-setuptools build-essential libfreetype6 libfreetype6-dev zlib1g-dev libjpeg62 libjpeg62-dev python-pip python-dev python-numpy python-scipy python-matplotlib python-imaging pkg-config libblas-dev liblapack-dev gfortran apache2

a2enmod wsgi

virtualenv venv && source ./venv/bin/activate

cat requirements.txt
flask
ete2
Pillow
Image
sqlalchemy
numpy
scipy
matplotlib
#MySQL-python


pip install --requirement requirements.txt #(takes a while)

cd data && scp -c arcfour assembly@assembly:/home/assembly/tomato150/programs/iBrowser/iBrowser.data.tar.gz . && tar xvzf iBrowser.data.tar.gz && rm iBrowser.data.tar.gz && cd - python ibrowser.py

ln -s ibrowser.conf /etc/apache2/mods-available/ibrowser.conf
