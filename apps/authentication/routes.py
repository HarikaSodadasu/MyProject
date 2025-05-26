# -*- encoding: utf-8 -*-
from flask import (
    render_template, redirect, request, url_for, session, jsonify
)
from flask_login import current_user, login_user, logout_user
from apps import db, login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm, CreateAccountForm
from apps.authentication.models import Users
from apps.authentication.util import verify_pass

from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import os
import socket
from dotenv import load_dotenv

# Load environment and setup MongoDB
load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db_mongo = client['virtual_Presenz']

# Collections
login_logs_collection = db_mongo['login_logs']
camera_collection = db_mongo['cameras']

# -------------- Camera Setup API Routes --------------

@blueprint.route('/add-camera', methods=['POST'])
def add_camera():
    try:
        data = request.get_json()
        camera_data = {
            'name': data.get('name'),
            'serial_number': data.get('serial_number'),
            'model': data.get('model'),
            'model_specific': data.get('model_specific'),
            'ip_address': data.get('ip_address'),
            'mac_address': data.get('mac_address'),
            'rtsp_link': data.get('rtsp_link')
        }
        camera_collection.insert_one(camera_data)
        return jsonify({'success': True, 'message': 'Camera added successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error adding camera: {str(e)}'}), 500


@blueprint.route('/get-cameras', methods=['GET'])
def get_cameras():
    try:
        cameras = list(camera_collection.find())
        for camera in cameras:
            camera['_id'] = str(camera['_id'])  # Convert ObjectId to string for JSON
        return jsonify({'success': True, 'cameras': cameras})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error fetching cameras: {str(e)}'}), 500


@blueprint.route('/update-camera/<camera_id>', methods=['PUT'])
def update_camera(camera_id):
    try:
        data = request.get_json()
        update_fields = {
            'name': data.get('name'),
            'serial_number': data.get('serial_number'),
            'model': data.get('model'),
            'model_specific': data.get('model_specific'),
            'ip_address': data.get('ip_address'),
            'mac_address': data.get('mac_address'),
            'rtsp_link': data.get('rtsp_link')
        }
        camera_collection.update_one(
            {"_id": ObjectId(camera_id)},
            {"$set": update_fields}
        )
        return jsonify({'success': True, 'message': 'Camera updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error updating camera: {str(e)}'}), 500


@blueprint.route('/delete-camera/<camera_id>', methods=['DELETE'])
def delete_camera(camera_id):
    try:
        result = camera_collection.delete_one({'_id': ObjectId(camera_id)})
        if result.deleted_count == 1:
            return jsonify({'success': True, 'message': 'Camera deleted'})
        else:
            return jsonify({'success': False, 'message': 'Camera not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error deleting camera: {str(e)}'}), 500


# -------------- Session Timeout Handling --------------

@blueprint.before_app_request
def track_user_activity():
    if current_user.is_authenticated:
        now = datetime.utcnow()
        last_active = session.get('last_active')

        # 30 minutes timeout threshold
        timeout_minutes = 30
        if last_active:
            last_active_dt = datetime.fromisoformat(last_active)
            if (now - last_active_dt) > timedelta(minutes=timeout_minutes):
                # Timeout detected
                log_id = session.pop('log_id', None)
                login_time = session.pop('login_time', None)
                session.clear()

                if log_id and login_time:
                    login_time_dt = datetime.fromisoformat(login_time)
                    session_duration = now - login_time_dt
                    minutes, seconds = divmod(int(session_duration.total_seconds()), 60)
                    duration_str = f"Timed out: {minutes}m {seconds}s"

                    login_logs_collection.update_one(
                        {"_id": ObjectId(log_id)},
                        {"$set": {
                            "logout_time": now,
                            "performance": duration_str
                        }}
                    )
                logout_user()
                return redirect(url_for('authentication_blueprint.login'))

        session['last_active'] = now.isoformat()


# -------------- Default and Authentication Routes --------------

@blueprint.route('/')
def route_default():
    if current_user.is_authenticated:
        return redirect(url_for('home_blueprint.index'))
    return redirect(url_for('authentication_blueprint.login'))


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)

    if 'login' in request.form:
        username = request.form['username']
        password = request.form['password']

        user = Users.query.filter_by(username=username).first()

        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip and ',' in ip:
            ip = ip.split(',')[0].strip()
        machine_name = socket.gethostname()

        login_time = datetime.utcnow()

        log_data = {
            "username": username,
            "login_time": login_time,
            "ip_address": ip,
            "machine_name": machine_name,
            "service_name": "Authentication",
            "logout_time": None,
            "performance": "Normal"
        }

        if user and verify_pass(password, user.password):
            login_user(user)

            log_data["message"] = "Login Successful"
            log_data["performance"] = "Active"

            inserted_log = login_logs_collection.insert_one(log_data)
            session['log_id'] = str(inserted_log.inserted_id)
            session['login_time'] = login_time.isoformat()
            session['last_active'] = login_time.isoformat()

            # Redirect to home/dashboard after login
            return redirect(url_for('home_blueprint.index'))
        else:
            log_data["message"] = "Login Failed"
            log_data["performance"] = "Failed"
            login_logs_collection.insert_one(log_data)

            return render_template('accounts/login.html',
                                   msg='Wrong user or password',
                                   form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html', form=login_form)

    return redirect(url_for('home_blueprint.index'))


@blueprint.route('/logout')
def logout():
    log_id = session.pop('log_id', None)
    login_time = session.pop('login_time', None)

    if log_id and login_time:
        try:
            logout_time = datetime.utcnow()
            login_time_dt = datetime.fromisoformat(login_time)
            session_duration = logout_time - login_time_dt
            minutes, seconds = divmod(int(session_duration.total_seconds()), 60)
            duration_str = f"Session ended: {minutes}m {seconds}s"

            login_logs_collection.update_one(
                {"_id": ObjectId(log_id)},
                {"$set": {
                    "logout_time": logout_time,
                    "performance": duration_str
                }}
            )
        except Exception as e:
            print("Logout Logging Error:", e)

    logout_user()
    session.clear()
    return redirect(url_for('authentication_blueprint.login'))


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    create_account_form = CreateAccountForm(request.form)

    if 'register' in request.form:
        username = request.form['username']
        email = request.form['email']

        if Users.query.filter_by(username=username).first():
            return render_template('accounts/register.html',
                                   msg='Username already registered',
                                   success=False,
                                   form=create_account_form)

        if Users.query.filter_by(email=email).first():
            return render_template('accounts/register.html',
                                   msg='Email already registered',
                                   success=False,
                                   form=create_account_form)

        user = Users(**request.form)
        db.session.add(user)
        db.session.commit()

        logout_user()

        return render_template('accounts/register.html',
                               msg='Account created successfully.',
                               success=True,
                               form=create_account_form)

    return render_template('accounts/register.html', form=create_account_form)


# -------------- Logs Display Route --------------

@blueprint.route('/logs')
def logs():
    logs = []
    for log in login_logs_collection.find():
        logs.append({
            "_id": str(log.get("_id")),
            "login_time": log.get("login_time"),
            "logout_time": log.get("logout_time"),
            "sequence": log.get("sequence", ""),
            "message": log.get("message", ""),
            "service_name": log.get("service_name", ""),
            "machine_name": log.get("machine_name", ""),
            "ip_address": log.get("ip_address", ""),
            "user": log.get("username", ""),
            "performance": log.get("performance", "")
        })

    return render_template('admin/logs.html', logs=logs)


# -------------- Unauthorized and Error Handlers --------------

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500
