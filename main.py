import os
from threading import active_count

import pandas as pd
from flask import Flask, render_template, redirect, url_for, flash, request, send_from_directory,session
from flask_bootstrap import Bootstrap

from sqlalchemy import ForeignKey
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

from flask_migrate import Migrate

from routes.analysis import analysis_bp
from routes.dashbord import dashboard_bp
from routes.entry import entry_bp
from routes.exit import exit_bp
from routes.profile import profile_bp
from routes.search import search_bp
from routes.select_entrypoint import entrypoint_bp
from routes.analysis2 import analysis2_bp
from routes.fingerprint_bp import fingerprint_bp
from routes.face import face_bp

from models import db

server_started = True

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sectrekey2346387'

# use this database uri for sqlite
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crowdmanagement.db?check_same_thread=False'

# and this one is for postgres
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://postgres:jitu123@localhost:5432/crowd_db"



db.init_app(app)
Bootstrap(app)

app.register_blueprint(analysis_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(entry_bp)
app.register_blueprint(exit_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(search_bp)
app.register_blueprint(entrypoint_bp)
app.register_blueprint(analysis2_bp)
app.register_blueprint(fingerprint_bp)
app.register_blueprint(face_bp)

@app.before_request
def clear_session_on_restart():
    global server_started
    if server_started :
        session.pop("entry_point", None)
        server_started = False

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=3000,debug = True)