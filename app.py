from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from python_files.spam_text import spam_text  # your logic
from python_files.deepfake_image import deepfake_image  # your logic
from python_files.deepfake_video import deepfake_video  # if you have this
import os
import secrets

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(16)

from flask import send_from_directory

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

# MySQL config (update with your credentials)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'spamwatchuser'
app.config['MYSQL_PASSWORD'] = 'StrongPassword123!'
app.config['MYSQL_DB'] = 'spamwatchdb'

mysql = MySQL(app)

from datetime import datetime
from flask import jsonify

def start_session_timer(email):
    cur = mysql.connection.cursor()
    login_time = datetime.now()
    cur.execute("INSERT INTO user_sessions (user_email, login_time) VALUES (%s, %s)", (email, login_time))
    mysql.connection.commit()
    cur.close()

def stop_session_timer(email):
    cur = mysql.connection.cursor()
    logout_time = datetime.now()
    # Update the latest session with null logout_time for this user
    cur.execute("UPDATE user_sessions SET logout_time=%s WHERE user_email=%s AND logout_time IS NULL", (logout_time, email))
    mysql.connection.commit()
    cur.close()

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form.get('confirm_password')
        if confirm_password is not None and password != confirm_password:
            return render_template('signup.html', error="Passwords do not match")
        cur = mysql.connection.cursor()
        # Check if user already exists
        cur.execute("SELECT email FROM users WHERE email=%s", (email,))
        existing_user = cur.fetchone()
        if existing_user:
            cur.close()
            return render_template('signup.html', error="User already exists. Please login.")
        hash_pass = generate_password_hash(password)
        try:
            cur.execute("INSERT INTO users (email, password_hash) VALUES (%s, %s)", (email, hash_pass))
            mysql.connection.commit()
            # Start session timer and set session
            start_session_timer(email)
            session['email'] = email
        except Exception as e:
            cur.close()
            return render_template('signup.html', error=f"Signup failed: {str(e)}")
        cur.close()
        return redirect(url_for('tools'))
    else:
        # If GET request, just render signup page
        return render_template('signup.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT password_hash FROM users WHERE email=%s", [email])
            user = cur.fetchone()
            cur.close()
        except Exception as e:
            return render_template('login.html', error=f"Database error: {str(e)}")
        if user:
            if check_password_hash(user[0], password):
                # Start session timer and set session
                start_session_timer(email)
                session['email'] = email
                return redirect(url_for('tools'))
            else:
                error_msg = "Invalid password"
                return render_template('login.html',error=error_msg)
        else:
            error_msg = "User does not exist"
            return render_template('login.html',error=error_msg)
    return render_template('login.html')

@app.route('/logout')
def logout():
    email = session.get('email')
    if email:
        stop_session_timer(email)
    session.clear()
    return redirect(url_for('login'))

@app.route('/result')
def result():
    # This route is for direct result page access if needed
    return render_template('result.html')

@app.route('/tools')
def tools():
    return render_template('tools.html')

@app.route('/spam_text', methods=['GET', 'POST'])
def spam_text_route():
    result = None
    score = None
    if request.method == 'POST':
        user_text = request.form['text']
        from python_files.spam_text import spam_text as spam_text_func
        result, score = spam_text_func(user_text)
        # Log user activity
        email = session.get('email')
        if email:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO tool_usage (user_email, tool_name, usage_time) VALUES (%s, %s, NOW())", (email, 'spam_text'))
            mysql.connection.commit()
            cur.close()
    return render_template('spam_text.html', result=result, score=score)

from flask import flash

import uuid
import os

@app.route('/deepfake_image', methods=['GET', 'POST'])
def deepfake_image_route():
    from flask import make_response
    result = None
    score = None
    image_url = None
    if request.method == 'POST':
        file = request.files.get('image')
        if not file:
            flash("No image file uploaded", "error")
            response = render_template('deepfake_image.html', result=result, score=score, image_url=image_url)
            resp = make_response(response)
            resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            resp.headers['Pragma'] = 'no-cache'
            resp.headers['Expires'] = '0'
            return resp
        filename = f"input_{uuid.uuid4().hex}.jpg"
        file_path = os.path.join('uploads', filename)
        try:
            file.save(file_path)
            image_url = file_path
        except Exception as e:
            flash(f"Failed to save image file: {e}", "error")
            response = render_template('deepfake_image.html', result=result, score=score, image_url=image_url)
            resp = make_response(response)
            resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            resp.headers['Pragma'] = 'no-cache'
            resp.headers['Expires'] = '0'
            return resp
        from python_files.deepfake_image import deepfake_image as deepfake_image_func
        try:
            print("DEBUG: Calling deepfake_image_func")
            result, score = deepfake_image_func(file_path)
            print(f"DEBUG: Detection result: {result}, score: {score}")
            if not result:
                flash("Detection failed to return a valid result", "error")
        except Exception as e:
            flash(f"Error in deepfake_image_func: {e}", "error")
            result = None
            score = None
        # Log user activity and save analysis result only if logged in
        email = session.get('email')
        print(f"DEBUG: User email from session: {email}")
        if email:
            try:
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO tool_usage (user_email, tool_name, usage_time) VALUES (%s, %s, NOW())", (email, 'deepfake_image'))
                cur.execute("INSERT INTO deepfake_image_results (user_email, result, confidence, analysis_time) VALUES (%s, %s, %s, NOW())", (email, result, score))
                mysql.connection.commit()
                cur.close()
                print("DEBUG: Logged usage and saved result to DB")
            except Exception as e:
                flash(f"Failed to log usage or save result: {e}", "error")
        else:
            print("DEBUG: User not logged in, skipping DB logging")
    response = render_template('deepfake_image.html', result=result, score=score, image_url=image_url)
    resp = make_response(response)
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

@app.route('/deepfake_video', methods=['GET', 'POST'])
def deepfake_video_route():
    from flask import make_response
    result = None
    score = None
    video_url = None
    if request.method == 'POST':
        file = request.files.get('video')
        if not file:
            flash("No video file uploaded", "error")
            response = render_template('deepfake_video.html', result=result, score=score, video_url=video_url)
            resp = make_response(response)
            resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            resp.headers['Pragma'] = 'no-cache'
            resp.headers['Expires'] = '0'
            return resp
        filename = f"input_{uuid.uuid4().hex}.mp4"
        file_path = os.path.join('uploads', filename)
        try:
            file.save(file_path)
            video_url = file_path
        except Exception as e:
            flash(f"Failed to save video file: {e}", "error")
            response = render_template('deepfake_video.html', result=result, score=score, video_url=video_url)
            resp = make_response(response)
            resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            resp.headers['Pragma'] = 'no-cache'
            resp.headers['Expires'] = '0'
            return resp
        from python_files.deepfake_video import deepfake_video as deepfake_video_func
        try:
            result, score = deepfake_video_func(file_path)
            print(f"DEBUG: Detection result: {result}, score: {score}")
            if not result:
                flash("Detection failed to return a valid result", "error")
        except Exception as e:
            flash(f"Error in deepfake_video_func: {e}", "error")
            result = None
            score = None
        # Log user activity and save analysis result
        email = session.get('email')
        if email:
            try:
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO tool_usage (user_email, tool_name, usage_time) VALUES (%s, %s, NOW())", (email, 'deepfake_video'))
                cur.execute("INSERT INTO deepfake_video_results (user_email, result, confidence, analysis_time) VALUES (%s, %s, %s, NOW())", (email, result, score))
                mysql.connection.commit()
                cur.close()
            except Exception as e:
                flash(f"Failed to log usage or save result: {e}", "error")
    response = render_template('deepfake_video.html', result=result, score=score, video_url=video_url)
    resp = make_response(response)
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

@app.route('/stop_session', methods=['POST'])
def stop_session():
    email = session.get('email')
    if email:
        stop_session_timer(email)
        session.clear()
        return jsonify({'status': 'session stopped'})
    return jsonify({'status': 'no active session'}), 400

if __name__ == '__main__':
    app.run(debug=True)
