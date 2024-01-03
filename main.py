from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
import firebase_admin
from firebase_admin import credentials, db, storage

app = Flask(__name__)
app.secret_key = 'back_to_the_future'

cred = credentials.Certificate("./credentials.json")
firebase_admin.initialize_app(cred, {'databaseURL': 'https://mobileproject-f497e-default-rtdb.firebaseio.com/'})

@app.before_request
def check_authentication():
    # List of routes that can be accessed without authentication
    allowed_routes = ['sign_up', 'sign_in']

    # If the requested route requires authentication and the user is not authenticated, redirect to the sign-in page
    if request.endpoint and request.endpoint not in allowed_routes and 'username' not in session:
        flash('Please sign in first', 'error')
        return redirect(url_for('sign_in'))

@app.route('/')
def sign_in():
    return render_template('sign_in.html')

@app.route('/sign_in/<username>', methods = ['GET'])
def signin(username):
    # Create a reference to the 'users' node in the database
    users_ref = db.reference('users')

    # Create a reference to the specific user using the provided username
    user_ref = users_ref.child(username)

    # Retrieve the user data
    user_data = user_ref.get()

    if user_data:
        session['username'] = username
        return jsonify({"user": user_data})
    else:
        return jsonify({"error": "User not found"}), 404

@app.route('/signup')
def sign_up():
    return render_template('sign_up.html')

@app.route('/sign_up', methods = ['POST'])
def signup():
    data = request.get_json()

    #Extract the name and replace any empty characters
    name = data.get('name')
    name_key = name.replace(' ', '_')

    #Create a reference using the name as the key
    users_ref = db.reference('users').child(name_key)

    # Check if the user already exists
    existing_user = users_ref.get()
    if existing_user:
        return jsonify({"error": "User already exists with the same name"})

    #Store user data
    userType = data.get('userType')
    new_user_ref = users_ref.set({
        'name': name,
        'pwd': data.get('pwd'),
        'userType': userType,
        'application': False if userType == 'emp' else None,  # For emp, set application to False; for hr, don't set it
        'opening': False if userType == 'hr' else None  # For hr, set opening to False; for emp, don't set it
    })
    return jsonify({"message": "Data stored successfully", "user_id": name_key})

@app.route('/home')
def home(username=None):
    # Check if the user is signed in
    if 'username' not in session:
        flash('Please sign in first', 'error')
        return redirect(url_for('sign_in'))

    # Retrieve the user data
    user_ref = get_user()
    user_data = user_ref.get()
    user_type = user_data.get('userType')

    # If a specific username is provided in the URL, use that, otherwise use the one from the session
    username_to_display = username or user_data.get('name')
    
    # Render the home template with the username
    if user_type == "hr":
        return render_template('index_hr.html', username=username_to_display)
    elif user_type == "emp":
        return render_template('index_emp.html', username=username_to_display)
    else:
        flash('User type not found', 'error')
        return redirect(url_for('sign_in'))

@app.route('/resume')
def resume_submission():
    return render_template('resume_submission.html')

@app.route('/application')
def application():
    return render_template('application.html')

@app.route('/submit_application', methods = ['POST'])
def submit_application():
    if 'username' not in session:
        flash('Please sign in first', 'error')
        return redirect(url_for('sign_in'))
    
    # Update the 'application' field to True
    user_ref = get_user()
    user_ref.update({'application': True})
    return jsonify({"message": "Application submitted successfully"})
    
@app.route('/my_application')
def my_application():
    # Check if the user is signed in
    if 'username' not in session:
        flash('Please sign in first', 'error')
        return redirect(url_for('sign_in'))

    # Fetch the application status from the database using the username
    user_ref = get_user()
    application_status = user_ref.get('application', False)
    print(session['username'])
    print(application_status)

    return render_template('apply_history.html', application_status = application_status)

@app.route('/job_opening')
def job_opening():
    return render_template('opening.html') 

@app.route('/publish_job', methods = ['POST'])
def publish_job():
    if 'username' not in session:
        flash('Please sign in first', 'error')
        return redirect(url_for('sign_in'))
    
    # Update the 'application' field to True
    user_ref = get_user()
    user_ref.update({'opening': True})
    return jsonify({"message": "Job opening published successfully"})      

def get_user():
    # Get the user from the session
    current_username = session['username']
    name_key = current_username.replace(' ', '_')
    
    # Create a reference to the 'users' node in the database
    users_ref = db.reference('users')

    # Create a reference to the specific user using the provided username
    user_ref = users_ref.child(name_key)
    return user_ref    

if __name__ == "__main__":
    app.run(debug=True)
