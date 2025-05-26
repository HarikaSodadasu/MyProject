# -*- encoding: utf-8 -*-

from apps.home import blueprint
from flask import render_template, request, flash, url_for, redirect
from flask_login import login_required
from jinja2 import TemplateNotFound
from pymongo import MongoClient
from dotenv import load_dotenv
import os

from datetime import datetime

# Setup MongoDB
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client['virtual_Presenz']
users_collection = db['users']
login_logs_collection = db['login_logs']  # NEW

@blueprint.route('/index')
@login_required
def index():
    return render_template('home/index.html', segment='index')


@blueprint.route('/<template>')
@login_required
def route_template(template):
    try:
        if not template.endswith('.html'):
            template += '.html'
        segment = get_segment(request)
        return render_template("home/" + template, segment=segment)
    except TemplateNotFound:
        return render_template('home/page-404.html'), 404
    except:
        return render_template('home/page-500.html'), 500


def get_segment(request):
    try:
        segment = request.path.split('/')[-1]
        if segment == '':
            segment = 'index'
        return segment
    except:
        return None


@blueprint.route('/add_user', methods=['POST'])
@login_required
def add_user():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirmPassword')
    role = request.form.get('role')

    if not all([username, email, password, confirm_password, role]):
        flash("All fields are required", "error")
        return redirect(url_for('home_blueprint.manage_users'))

    if password != confirm_password:
        return "Passwords do not match", 400

    if users_collection.find_one({"email": email}):
        flash("A user with this email already exists", "error")
        return redirect(url_for('home_blueprint.manage_users'))

    user = {
        "username": username,
        "email": email,
        "password": password,
        "role": role
    }
    users_collection.insert_one(user)
    flash("User added successfully!", "success")
    return redirect('/admin')


@blueprint.route('/admin', methods=['GET'])
@login_required
def manage_users():
    users = list(users_collection.find())
    login_logs = list(login_logs_collection.find().sort("login_time", -1))  # NEW: fetch logs
    return render_template('home/admin.html', users=users, login_logs=login_logs)  # send logs to template


@blueprint.route('/delete_user', methods=['POST'])
@login_required
def delete_user():
    email = request.form.get('email')
    if not email:
        flash("No user email provided", "error")
        return redirect(url_for('home_blueprint.manage_users'))

    result = users_collection.delete_one({"email": email})
    if result.deleted_count == 1:
        flash("User deleted successfully!", "success")
    else:
        flash("User not found", "error")

    return redirect(url_for('home_blueprint.manage_users'))
