import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Render पर डेटाबेस को सुरक्षित रखने का सही तरीका
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'neelam.db')
app.config['SECRET_KEY'] = 'neelam_electronics_secret_key'
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static/uploads')

db = SQLAlchemy(app)