from flask import Flask, request, jsonify
from flask import render_template
from flask import session, redirect, url_for, flash
import firebase_admin
from firebase_admin import credentials, db, storage

app = Flask(__name__)
app.secret_key = 'back_to_the_future'

cred = credentials.Certificate("./credentials.json")
firebase_admin.initialize_app(cred, {'databaseURL': 'https://mobileproject-f497e-default-rtdb.firebaseio.com/'})
#firebase_storage = storage.bucket(app = firebase_admin.get_app())

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
        session['username'] = user_data.get('name')
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
    new_user_ref = users_ref.set({
        'name': name,
        'pwd': data.get('pwd'),
        'userType': data.get('userType')
    })
    return jsonify({"message": "Data stored successfully", "user_id": name_key})


@app.route('/home')
def home(username=None):
    # Check if the user is signed in
    if 'username' not in session:
        flash('Please sign in first', 'error')
        return redirect(url_for('sign_in'))

    # Get the username from the session
    current_username = session['username']

    # If a specific username is provided in the URL, use that, otherwise use the one from the session
    username_to_display = username or current_username

    # Render the home template with the username
    return render_template('index_emp.html', username=username_to_display)

@app.route('/resume')
def resume_submission():
    return render_template('resume_submission.html')

if __name__ == "__main__":
    app.run(debug=True)
