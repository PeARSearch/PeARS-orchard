# Import flask and template operators
from flask import Flask, render_template
from flask_admin import Admin

# Import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('config')

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)

# Sample HTTP error handling
#@app.errorhandler(404)
#def not_found(error):
#    return render_template('404.html'), 404

# Import a module / component using its blueprint handler variable (mod_auth)
from app.indexer.controllers import indexer as indexer_module
from app.api.controllers import api as api_module
from app.search.controllers import search as search_module
from app.pod_finder.controllers import pod_finder as pod_finder_module
from app.orchard.controllers import orchard as orchard_module
from app.pages.controllers import pages as pages_module

# Register blueprint(s)
app.register_blueprint(indexer_module)
app.register_blueprint(api_module)
app.register_blueprint(search_module)
app.register_blueprint(pod_finder_module)
app.register_blueprint(orchard_module)
app.register_blueprint(pages_module)
# ..

# Build the database:
# This will create the database file using SQLAlchemy
# db.drop_all()
db.create_all()

from flask_admin.contrib.sqla import ModelView
from app.api.models import Pods,Urls

# Flask and Flask-SQLAlchemy initialization here

admin = Admin(app, name='PeARS DB', template_mode='bootstrap3')

class UrlsModelView(ModelView):
    list_template = 'admin/pears_list.html'
    column_exclude_list = ['vector','freqs']
    column_searchable_list = ['url', 'title', 'keyword', 'pod']
    column_editable_list = ['keyword']
    can_edit = False
    page_size = 50

class PodsModelView(ModelView):
    list_template = 'admin/pears_list.html'
    column_exclude_list = ['DS_vector','word_vector']
    column_searchable_list = ['url', 'name', 'description', 'language']
    can_edit = False
    page_size = 50

admin.add_view(PodsModelView(Pods, db.session))
admin.add_view(UrlsModelView(Urls, db.session))
