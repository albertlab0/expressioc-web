from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os 

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
    return "Hello from Flask."

@app.route('/upload')
def upload_file():
   return render_template('upload.html')


UPLOAD_FOLDER = "./samples/"

@app.route('/uploader', methods = ['GET', 'POST'])
def handle_file():
   if request.method == 'POST':
      f = request.files['file']
      f.save(os.path.join(UPLOAD_FOLDER, secure_filename(f.filename)))
      return 'file uploaded successfully'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555)
