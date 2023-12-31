from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
import firebase_admin
from firebase_admin import credentials, db
from server1 import grade 

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'back_to_the_future'

cred = credentials.Certificate("./mobileproject-f497e-firebase-adminsdk-q9hdw-d87f5e31b5.json")
firebase_admin.initialize_app(cred, {'databaseURL': 'https://mobileproject-f497e-default-rtdb.firebaseio.com/'})


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
    users_ref.set({
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
        # Fetch the job opening publish from the database using the username
        user_ref = get_user()
        user_data = user_ref.get()
        opening = user_data.get('opening')
        return render_template('index_hr.html', username=username_to_display, opening = opening)
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
    
    # Get the user data
    user_ref = get_user()
    user_ref.update({'application': True})
    data = request.get_json()
    resume_link = data.get('resume')
    grade_obtain = grade()
    
    # Keep track of candidates for the application
    name = user_ref.get().get('name')
    name_key = name.replace(' ', '_')
    app_ref = db.reference('application').child(name_key)
    app_ref.set({'name': name, 'resume': resume_link, 'grade': grade_obtain, 'status': 'In progress'})
    return jsonify({"message": "Application submitted successfully"})
    
@app.route('/my_application')
def my_application():
    # Check if the user is signed in
    if 'username' not in session:
        flash('Please sign in first', 'error')
        return redirect(url_for('sign_in'))

    # Fetch the application status from the database using the username
    username = session['username']
    app_ref = get_candidate(username)
    
    if app_ref:
        app_data = app_ref.get()
        application_status = app_data.get('status', 'In progress')
    else:
        application_status = None
    
    return render_template('apply_history.html', application = application_status)

@app.route('/job_opening')
def job_opening():
    return render_template('opening.html') 

@app.route('/publish_job', methods = ['POST'])
def publish_job():
    if 'username' not in session:
        flash('Please sign in first', 'error')
        return redirect(url_for('sign_in'))
    
    # Update the 'opening' field to True
    user_ref = get_user()
    user_ref.update({'opening': True})
    return jsonify({"message": "Job opening published successfully"})

@app.route('/candidates')
def candidates():
    candidate = db.reference('application')
    candidate_data = candidate.get()
    return render_template('candidate.html', candidates = candidate_data) 

@app.route('/update_status', methods = ['POST'])
def update_status():
    status = request.form.get('status')
    candidate_name = request.form.get('candidateName')
    
    candidate_ref = get_candidate(candidate_name)
    
    candidate_ref.update({'status': status})
    return jsonify({"message": "Candidate status updated successfully"})

def get_user():
    # Get the user from the session
    current_username = session['username']
    name_key = current_username.replace(' ', '_')
    
    # Create a reference to the 'users' node in the database
    users_ref = db.reference('users')

    # Create a reference to the specific user using the provided username
    user_ref = users_ref.child(name_key)
    return user_ref

def get_candidate(name):
    # Get the candidate data
    candidate_key = name.replace(' ', '_')
    candidate_ref = db.reference('application').child(candidate_key)
    return candidate_ref
    

if __name__ == "__main__":
    app.run(debug=True)
