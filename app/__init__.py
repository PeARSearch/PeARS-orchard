# SPDX-FileCopyrightText: 2022 Aurelie Herbelot, <aurelie.herbelot@unitn.it>, 
#
# SPDX-License-Identifier: AGPL-3.0-only

# import logging 
import logging

# Import flask and template operators
from flask import Flask, render_template
from flask_admin import Admin

# Import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy


def configure_logging():
    # register root logging
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('werkzeug').setLevel(logging.INFO)


configure_logging()

# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('config')

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)


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
from app.api.models import Pods, Urls

# Flask and Flask-SQLAlchemy initialization here

admin = Admin(app, name='PeARS DB', template_mode='bootstrap3')

class UrlsModelView(ModelView):
    list_template = 'admin/pears_list.html'
    column_exclude_list = ['vector']
    column_searchable_list = ['url', 'title', 'notes', 'pod']
    column_editable_list = ['notes']
    can_edit = True
    page_size = 50
    form_widget_args = {
        'vector': {
            'readonly': True
        },
        'date_created': {
            'readonly': True
        },
        'date_modified': {
            'readonly': True
        },
    }

class PodsModelView(ModelView):
    list_template = 'admin/pears_list.html'
    column_exclude_list = ['DS_vector','word_vector']
    column_searchable_list = ['url', 'name', 'description', 'language']
    can_edit = True
    page_size = 50
    form_widget_args = {
        'DS_vector': {
            'readonly': True
        },
        'word_vector': {
            'readonly': True
        },
        'date_created': {
            'readonly': True
        },
        'date_modified': {
            'readonly': True
        },
    }

admin.add_view(PodsModelView(Pods, db.session))
admin.add_view(UrlsModelView(Urls, db.session))
