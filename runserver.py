from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os 

GHIDRA_HEADLESS= "C:\\ghidra_10.1.4_PUBLIC\\support\\analyzeHeadless.bat"

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
      filename = os.path.join(UPLOAD_FOLDER, secure_filename(f.filename))
      f.save(filename)
      command1 = "withdll.exe /d:expressioc.dll c:\\windows\system32\\regsvr32.exe %s" %filename
      os.system(command1)
      command2 = GHIDRA_HEADLESS + " . temp1 -import dump_0.bin -postscript emotet_new.py"
      os.system(command2)
      with open("c2.txt") as f:
          data = f.read()
      lines = data.split("\n")
      return "command1=%s<p> command2=%s<p>IOC:<p>%s" %(command1, command2, "<p>".join(lines))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555)
