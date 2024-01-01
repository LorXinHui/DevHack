from flask import Flask, request, jsonify
from flask import render_template
import firebase_admin
from firebase_admin import credentials, db, storage

app = Flask(__name__)
app.secret_key = 'back_to_the_future'

cred = credentials.Certificate("./credentials.json")
firebase_admin.initialize_app(cred, {'databaseURL': 'https://mobileproject-f497e-default-rtdb.firebaseio.com/'})
#firebase_storage = storage.bucket(app = firebase_admin.get_app())

@app.route('/')
def sign_up():
    return render_template('sign_up.html')

@app.route('/signup', methods = ['POST'])
def signup():
    data = request.get_json()

    # Check if the data already exists in the database before adding a new entry
    users_ref = db.reference('users')
    new_user_ref = users_ref.push({
        'name': data.get('name'),
        'pwd': data.get('pwd'),
        'userType': data.get('userType')
    })

    return jsonify({"message": "Data stored successfully", "user_id": new_user_ref.key()})


@app.route('/home')
def resume_submission():
    # Push data to Firebase
    # ref = db.reference('/messages')
    # ref.push({'text': 'Hello, Firebase!'})
    return render_template('resume_submission.html')

@app.route('/messages')
def messages():
    # Retrieve data from Firebase
    ref = db.reference('/messages')
    messages = ref.get()

    return render_template('messages.html', messages=messages)

if __name__ == "__main__":
    app.run(debug=True)
