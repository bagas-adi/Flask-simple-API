from flask import Flask
import os
import sys
fn = getattr(sys.modules['__main__'], '__file__')
root_path = os.path.abspath(os.path.dirname(fn))
UPLOAD_FOLDER = root_path+'/img' #'C:/[ DATA (F)]/DemoVenv/flask/DemoUpload/img' #'http://localhost:5000/DemoUpload/img'

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024