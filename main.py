from flask import Flask, request
from flask import render_template

app = Flask(__name__)
app.secret_key = 'back_to_the_future'

import firebase_admin
from firebase_admin import credentials, db, storage
cred = credentials.Certificate("./credentials.json")
firebase_admin.initialize_app(cred, {'databaseURL': 'https://mobileproject-f497e-default-rtdb.firebaseio.com/'})
firebase_storage = storage.bucket(app = firebase_admin.get_app())

@app.route('/')
def resume_submission():
    return render_template('resume_submission.html')

@app.route('/upload', methods = ['POST'])
def upload_file():
    if 'resume' not in request.files:
        return "No file part"

    resume_file = request.files['resume']
    if resume_file.filename == '':
        return "No selected file"

    blob = firebase_storage.blob(resume_file.filename)
    blob.upload_from_file(resume_file)

    file_url = blob.public_url
    return f"File uploaded successfully. URL: {file_url}"

if __name__ == "__main__":
    app.run(debug=True)
