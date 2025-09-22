"""
Spamwatch.ai - A Flask web application for detecting spam text and deepfake media.

This application provides a web interface for users to:
- Analyze text messages for spam detection using machine learning
- Detect deepfake images using AI models
- Detect deepfake videos using AI models
- User authentication and session management
- Database logging of user activities and analysis results

The app uses Flask as the web framework, MySQL for data storage,
and integrates with various AI models for content analysis.
"""

# Standard library imports for core functionality
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL  # MySQL database connector for Flask
from werkzeug.security import generate_password_hash, check_password_hash  # Password hashing utilities
from python_files.spam_text import spam_text  # Spam detection function
from python_files.deepfake_image import deepfake_image  # Image deepfake detection function
from python_files.deepfake_video import deepfake_video  # Video deepfake detection function
import os  # Operating system interface
import secrets  # Generate secure random tokens

# Initialize Flask application instance
app = Flask(__name__)
# Set secret key for session management (use environment variable or generate random key)
app.secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(16)

# Import additional Flask utilities after app initialization
from flask import send_from_directory

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """
    Serve uploaded files from the uploads directory.

    This route allows the web application to serve files that users have uploaded
    for analysis, such as images and videos for deepfake detection.

    Args:
        filename (str): The name of the file to serve

    Returns:
        Response: The requested file from the uploads directory
    """
    return send_from_directory('uploads', filename)

# MySQL database configuration settings
# These settings connect the application to the MySQL database
app.config['MYSQL_HOST'] = 'localhost'  # Database server location
app.config['MYSQL_USER'] = 'spamwatchuser'  # Database username
app.config['MYSQL_PASSWORD'] = 'StrongPassword123!'  # Database password
app.config['MYSQL_DB'] = 'spamwatchdb'  # Database name

# Initialize MySQL extension for Flask
mysql = MySQL(app)

# Import datetime for timestamp functionality
from datetime import datetime

def start_session_timer(email):
    """
    Record the start time of a user session in the database.

    This function logs when a user logs in by inserting a record into
    the user_sessions table with their email and login timestamp.

    Args:
        email (str): The email address of the logged-in user

    Returns:
        None
    """
    # Create database cursor for executing queries
    cur = mysql.connection.cursor()
    # Get current timestamp for login time
    login_time = datetime.now()
    # Insert session record into database
    cur.execute("INSERT INTO user_sessions (user_email, login_time) VALUES (%s, %s)", (email, login_time))
    # Commit the transaction to save changes
    mysql.connection.commit()
    # Close cursor to free database resources
    cur.close()

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Handle user registration process.

    GET: Display the signup form
    POST: Process registration form data, validate input, create user account

    The function validates passwords match, checks for existing users,
    hashes passwords securely, and creates user sessions upon successful registration.

    Returns:
        Response: Rendered signup template or redirect to tools page
    """
    if request.method == 'POST':
        # Extract form data from user input
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form.get('confirm_password')

        # Validate that passwords match (if confirm password field exists)
        if confirm_password is not None and password != confirm_password:
            return render_template('signup.html', error="Passwords do not match")

        # Create database cursor for user queries
        cur = mysql.connection.cursor()
        # Check if user already exists in database
        cur.execute("SELECT email FROM users WHERE email=%s", (email,))
        existing_user = cur.fetchone()

        if existing_user:
            # Close cursor and return error if user exists
            cur.close()
            return render_template('signup.html', error="User already exists. Please login.")

        # Hash password for secure storage
        hash_pass = generate_password_hash(password)

        try:
            # Insert new user into database
            cur.execute("INSERT INTO users (email, password_hash) VALUES (%s, %s)", (email, hash_pass))
            mysql.connection.commit()
            # Start session timer and set user session
            start_session_timer(email)
            session['email'] = email
        except Exception as e:
            # Handle database errors during user creation
            cur.close()
            return render_template('signup.html', error=f"Signup failed: {str(e)}")

        # Close cursor and redirect to tools page
        cur.close()
        return redirect(url_for('tools'))
    else:
        # If GET request, just render signup page
        return render_template('signup.html')

@app.route('/')
def index():
    """
    Display the home page of the application.

    This is the main landing page that users see when they first visit
    the Spamwatch.ai website.

    Returns:
        Response: Rendered index.html template
    """
    return render_template('index.html')

@app.route('/about')
def about():
    """
    Display the about page with information about Spamwatch.ai.

    This page provides details about the application's purpose,
    features, and how it works.

    Returns:
        Response: Rendered about.html template
    """
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user authentication process.

    GET: Display the login form
    POST: Process login credentials, validate user, create session

    The function checks user credentials against the database,
    verifies password hashes, and creates user sessions upon successful login.

    Returns:
        Response: Rendered login template or redirect to tools page
    """
    if request.method == 'POST':
        # Extract login credentials from form
        email = request.form['email']
        password = request.form['password']

        try:
            # Create database cursor and query user data
            cur = mysql.connection.cursor()
            cur.execute("SELECT password_hash FROM users WHERE email=%s", [email])
            user = cur.fetchone()
            cur.close()
        except Exception as e:
            # Handle database connection errors
            return render_template('login.html', error=f"Database error: {str(e)}")

        if user:
            # Verify password against stored hash
            if check_password_hash(user[0], password):
                # Start session timer and set user session
                start_session_timer(email)
                session['email'] = email
                return redirect(url_for('tools'))
            else:
                # Return error for invalid password
                error_msg = "Invalid password"
                return render_template('login.html', error=error_msg)
        else:
            # Return error for non-existent user
            error_msg = "User does not exist"
            return render_template('login.html', error=error_msg)

    # Render login page for GET requests
    return render_template('login.html')

@app.route('/logout')
def logout():
    """
    Handle user logout process.

    This function clears the user's session data and redirects
    them back to the login page.

    Returns:
        Response: Redirect to login page
    """
    session.clear()
    return redirect(url_for('login'))

@app.route('/result')
def result():
    """
    Display the result page.

    This route provides access to a general results page that can be
    used to display analysis results or other information.

    Returns:
        Response: Rendered result.html template
    """
    return render_template('result.html')

@app.route('/tools')
def tools():
    """
    Display the tools page with available analysis options.

    This page shows users the different AI-powered tools available
    for content analysis (spam detection, deepfake detection, etc.).

    Returns:
        Response: Rendered tools.html template
    """
    return render_template('tools.html')

@app.route('/spam_text', methods=['GET', 'POST'])
def spam_text_route():
    """
    Handle spam text analysis requests.

    GET: Display the spam text analysis form
    POST: Process text input, run spam detection, log results

    This function takes user text input, runs it through the spam detection
    model, and stores the results in the database for logged-in users.

    Returns:
        Response: Rendered spam_text.html template with results
    """
    result = None  # Store analysis result (spam/ham)
    score = None   # Store confidence score

    if request.method == 'POST':
        # Get text input from user
        user_text = request.form['text']
        # Import and call spam detection function
        from python_files.spam_text import spam_text as spam_text_func
        result, score = spam_text_func(user_text)

        # Log user activity and save analysis result for logged-in users
        email = session.get('email')
        if email:
            cur = mysql.connection.cursor()
            # Record tool usage in database
            cur.execute("INSERT INTO tool_usage (user_email, tool_name, usage_time, confidence_score) VALUES (%s, %s, NOW(), %s)", (email, 'spam_text', score))
            # Save detailed analysis results
            cur.execute("INSERT INTO spam_text_results (user_email, result, confidence, analysis_time) VALUES (%s, %s, %s, NOW())", (email, result, score))
            mysql.connection.commit()
            cur.close()

    return render_template('spam_text.html', result=result, score=score)

# Import additional utilities for file handling
from flask import flash
import uuid  # Generate unique identifiers
import os   # File system operations

@app.route('/deepfake_image', methods=['GET', 'POST'])
def deepfake_image_route():
    """
    Handle deepfake image detection requests.

    GET: Display the image upload form
    POST: Process uploaded image, run deepfake detection, log results

    This function handles image file uploads, runs deepfake detection
    using AI models, and stores results in the database for logged-in users.

    Returns:
        Response: Rendered deepfake_image.html template with results
    """
    from flask import make_response

    result = None           # Store detection result (Real/Deepfake)
    score = None            # Store confidence score
    image_url = None        # Store path to uploaded image
    uploaded_filename = None # Store original filename

    if request.method == 'POST':
        # Get uploaded image file
        file = request.files.get('image')

        if not file:
            # Handle case where no file was uploaded
            flash("No image file uploaded", "error")
            response = render_template('deepfake_image.html', result=result, score=score, image_url=image_url, uploaded_filename=uploaded_filename)
            resp = make_response(response)
            resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            resp.headers['Pragma'] = 'no-cache'
            resp.headers['Expires'] = '0'
            return resp

        # Store original filename for display
        uploaded_filename = file.filename
        # Generate unique filename to prevent conflicts
        filename = f"input_{uuid.uuid4().hex}.jpg"
        # Create file path for saving uploaded image
        file_path = os.path.join('uploads', filename).replace('\\', '/')

        try:
            # Save uploaded file to server
            file.save(file_path)
            image_url = file_path
        except Exception as e:
            # Handle file save errors
            flash(f"Failed to save image file: {e}", "error")
            response = render_template('deepfake_image.html', result=result, score=score, image_url=image_url, uploaded_filename=uploaded_filename)
            resp = make_response(response)
            resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            resp.headers['Pragma'] = 'no-cache'
            resp.headers['Expires'] = '0'
            return resp

        # Import and run deepfake detection function
        from python_files.deepfake_image import deepfake_image as deepfake_image_func

        try:
            print("DEBUG: Calling deepfake_image_func")
            result, score = deepfake_image_func(file_path)
            print(f"DEBUG: Detection result: {result}, score: {score}")
            if not result:
                flash("Detection failed to return a valid result", "error")
        except Exception as e:
            # Handle detection errors
            flash(f"Error in deepfake_image_func: {e}", "error")
            result = None
            score = None

        # Log user activity and save analysis result only if logged in
        email = session.get('email')
        print(f"DEBUG: User email from session: {email}")

        if email:
            try:
                cur = mysql.connection.cursor()
                # Record tool usage
                cur.execute("INSERT INTO tool_usage (user_email, tool_name, usage_time, confidence_score) VALUES (%s, %s, NOW(), %s)", (email, 'deepfake_image', score))
                # Save detailed image analysis results
                cur.execute("INSERT INTO deepfake_image_results (user_email, result, confidence, analysis_time) VALUES (%s, %s, %s, NOW())", (email, result, score))
                mysql.connection.commit()
                cur.close()
                print("DEBUG: Logged usage and saved result to DB")
            except Exception as e:
                flash(f"Failed to log usage or save result: {e}", "error")
        else:
            print("DEBUG: User not logged in, skipping DB logging")

    # Prepare response with cache control headers to prevent caching
    response = render_template('deepfake_image.html', result=result, score=score, image_url=image_url, uploaded_filename=uploaded_filename)
    resp = make_response(response)
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

@app.route('/deepfake_video', methods=['GET', 'POST'])
def deepfake_video_route():
    """
    Handle deepfake video detection requests.

    GET: Display the video upload form
    POST: Process uploaded video, run deepfake detection, log results

    This function handles video file uploads, runs deepfake detection
    using AI models, and stores results in the database for logged-in users.

    Returns:
        Response: Rendered deepfake_video.html template with results
    """
    from flask import make_response

    result = None           # Store detection result (Real/Deepfake)
    score = None            # Store confidence score
    video_url = None        # Store path to uploaded video
    uploaded_filename = None # Store original filename

    if request.method == 'POST':
        # Get uploaded video file
        file = request.files.get('video')

        if not file:
            # Handle case where no file was uploaded
            flash("No video file uploaded", "error")
            response = render_template('deepfake_video.html', result=result, score=score, video_url=video_url, uploaded_filename=uploaded_filename)
            resp = make_response(response)
            resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            resp.headers['Pragma'] = 'no-cache'
            resp.headers['Expires'] = '0'
            return resp

        # Store original filename for display
        uploaded_filename = file.filename
        # Generate unique filename to prevent conflicts
        filename = f"input_{uuid.uuid4().hex}.mp4"
        # Create file path for saving uploaded video
        file_path = os.path.join('uploads', filename).replace('\\', '/')

        try:
            # Save uploaded file to server
            file.save(file_path)
            video_url = file_path
        except Exception as e:
            # Handle file save errors
            flash(f"Failed to save video file: {e}", "error")
            response = render_template('deepfake_video.html', result=result, score=score, video_url=video_url, uploaded_filename=uploaded_filename)
            resp = make_response(response)
            resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            resp.headers['Pragma'] = 'no-cache'
            resp.headers['Expires'] = '0'
            return resp

        # Import and run deepfake detection function
        from python_files.deepfake_video import deepfake_video as deepfake_video_func

        try:
            result, score = deepfake_video_func(file_path)
            print(f"DEBUG: Detection result: {result}, score: {score}")
            if not result:
                flash("Detection failed to return a valid result", "error")
        except Exception as e:
            # Handle detection errors
            flash(f"Error in deepfake_video_func: {e}", "error")
            result = None
            score = None

        # Log user activity and save analysis result for logged-in users
        email = session.get('email')
        if email:
            try:
                cur = mysql.connection.cursor()
                # Record tool usage
                cur.execute("INSERT INTO tool_usage (user_email, tool_name, usage_time, confidence_score) VALUES (%s, %s, NOW(), %s)", (email, 'deepfake_video', score))
                # Save detailed video analysis results
                cur.execute("INSERT INTO deepfake_video_results (user_email, result, confidence, analysis_time) VALUES (%s, %s, %s, NOW())", (email, result, score))
                mysql.connection.commit()
                cur.close()
            except Exception as e:
                flash(f"Failed to log usage or save result: {e}", "error")

    # Prepare response with cache control headers to prevent caching
    response = render_template('deepfake_video.html', result=result, score=score, video_url=video_url, uploaded_filename=uploaded_filename)
    resp = make_response(response)
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

# Main entry point - run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
