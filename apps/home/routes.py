# -*- encoding: utf-8 -*-

from apps.home import blueprint
from flask import render_template, request,flash, url_for
from flask_login import login_required
from jinja2 import TemplateNotFound
from pymongo import MongoClient
from dotenv import load_dotenv
from flask import Flask, request, redirect, render_template
import os

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client['virtual_Presenz']
users_collection = db['users']

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

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
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
    # Get form data
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

    # Save to MongoDB
    user = {
        "username": username,
        "email": email,
        "password": password,  # Consider hashing in production!
        "role": role
    }
    users_collection.insert_one(user)
    flash("User added successfully!", "success")
    return redirect('/admin')
@blueprint.route('/admin', methods=['GET'])
@login_required
def manage_users():
    from pymongo import MongoClient
    import os
    from dotenv import load_dotenv

    load_dotenv()
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client['virtual_Presenz']
    users_collection = db['users']
    #users_collection = mongo.db.users  # 'users' is your MongoDB collection name
    users = list(users_collection.find())  # Convert the cursor to a list
    print("Users fetched from DB:", users)
    return render_template('home/admin.html', users=users)
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
