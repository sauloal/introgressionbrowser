from flask.ext.sqlalchemy import SQLAlchemy
import hashlib
import random
import time
import sys
import os
from datetime import datetime

#from wtforms              import form, fields, validators

app.config['DATABASE_FILE'          ] = os.path.join( dir_path, 'users.sqlite' )
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_FILE']
app.config['SQLALCHEMY_ECHO'        ] = False

user_db = SQLAlchemy(app)



#https://github.com/mrjoes/flask-admin/blob/master/examples/auth/app.py
class User(user_db.Model):
    id         = user_db.Column(user_db.Integer, primary_key=True)
    first_name = user_db.Column(user_db.String(100))
    last_name  = user_db.Column(user_db.String(100))
    login      = user_db.Column(user_db.String( 80), unique=True)
    email      = user_db.Column(user_db.String(120))
    password   = user_db.Column(user_db.String(400))
    salt       = user_db.Column(user_db.String(400))

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return self.login





def check_user_exists(username):
    return user_db.session.query(User).filter_by(login=username).count() > 0



def get_user(username):
    return user_db.session.query(User).filter_by(login=username).first()



def get_users():
    users = [ x.login for x in User.query.order_by(User.login) ]
    users.sort()
    return users



def add_user(username, password, salt):
    if check_user_exists(username):
        raise KeyError

    user = User()

    user.login    = username
    user.password = password
    user.salt     = salt

    user_db.session.add(user)
    user_db.session.commit()



def get_salt(username):
    return get_user(username).salt



def verify_user_credentials(username, password, noonce):
    user = get_user( username )
    pwd  = user.password
    cry  = generate_password_hash(noonce+pwd)
    print "user %s pwd %s cry %s password %s" % ( user, pwd, cry, password )

    if cry == password:
        return True

    else:
        return False



def del_user(username):
    user = get_user(username)
    user_db.session.delete(user)
    user_db.session.commit()



def generate_password_hash(seq):
    return hashlib.sha384( seq ).hexdigest()



def gen_noonce():
    return generate_password_hash( str(random.randint(0, sys.maxint)) + str(time.time()) + str(datetime.now().microsecond) )


