from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os 
import sys
import logging
import shutil
import struct
import pefile

GHIDRA_HEADLESS= "C:\\ghidra_10.1.4_PUBLIC\\support\\analyzeHeadless.bat"

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
    return "Hello from Flask."

@app.route('/upload')
def upload_file():
   return render_template('upload.html')

# clean up existing Ghidra project file
def cleanup_temp_files():
    try:
        os.remove("dump*.bin")
        os.remove("virtualalloc*.bin")
        os.remove("c2.txt")
    except OSError as error:
        print(error)

def cleanup_project(proj_name):
    try:
        os.remove("%s.gpr" %proj_name)
        shutil.rmtree("%s.rep" %proj_name)
    except OSError as error:
        print(error)

UPLOAD_FOLDER = "./samples/"

def mylog(s):
    with(open("templog.txt", "a")) as f:
        f.write(s+"\n")

def emotet_old(filename, offset, size):
    mylog("offset=%x, size=%x" %(offset, size))
    with open(filename, "rb") as f:
        all_data = f.read()
        data = all_data[offset:offset + size]
        key,  = struct.unpack("L", data[:4])
        mylog(f"key=%x" %key)

        dec_len,  = struct.unpack("L", data[4:8])
        dec_len ^= key
        i = 8 

        ba = bytearray()
        while i <= dec_len + 4:
            dw,  = struct.unpack("L", data[i:i+4])
            dw ^= key
            ba4 = dw.to_bytes(4, byteorder="little")
            ba += ba4
            i += 4 

        i = 0
        ret = ""
        while i < len(ba):
            ip = f"{ba[i]}.{ba[i+1]}.{ba[i+2]}.{ba[i+3]}"
            port = (ba[i+4] << 8) | ba[i+5]
            ret += "{}:{}\n".format(ip, port)
            i += 8 
        with open("c2.txt", "w") as fout:
            fout.write(ret)

@app.route('/uploader', methods = ['GET', 'POST'])
def handle_file():
    if request.method == 'POST':
        f = request.files['file']
        filename = os.path.join(UPLOAD_FOLDER, secure_filename(f.filename))
        f.save(filename)
        command1 = "withdll.exe /d:expressioc.dll c:\\windows\system32\\regsvr32.exe %s" %filename
        os.system(command1)
        cleanup_project("temp1")
        cleanup_temp_files()
      
        pe = pefile.PE("dump_0.bin")
        if pe is None:
            return "Error"

        data_size = -1 
        for section in pe.sections:
            if section.Name[:5] == b".data":
                data_size = section.SizeOfRawData
                data_offset = section.PointerToRawData
        command2 = ""
        if data_size == 0:
            command2 = GHIDRA_HEADLESS + " . temp1 -import dump_0.bin -postscript emotet_new.py"
            os.system(command2)
        elif data_size > 0 :
            emotet_old("dump_0.bin", data_offset, data_size)
        else :
            return "Error"
        
        with open("c2.txt") as f:
            data = f.read()
        lines = data.split("\n")
        return "command1=%s<p> command2=%s<p>IOC:<p>%s" %(command1, command2, "<br>".join(lines))

if __name__ == '__main__':
    #logging.basicConfig(filename="debuglog.txt", filemode='a')
    app.run(host='0.0.0.0', port=5555)
