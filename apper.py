from flask       import Flask

app                                         = Flask(__name__)
app.jinja_env.globals['trim_blocks'       ] = True
app.jinja_env.add_extension('jinja2.ext.do')
app.config.from_object(__name__)
