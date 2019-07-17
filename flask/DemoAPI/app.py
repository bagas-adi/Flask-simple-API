from flask import Flask, render_template, request, json
from flaskext.mysql import MySQL
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask import request, jsonify
from flask_jwt_extended import (create_access_token, create_refresh_token,
jwt_required, jwt_refresh_token_required, get_jwt_identity)
import glob
import os
# import magic
import urllib
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
from datetime import datetime,timedelta
import sys

"""
TODO : 
1. coba JWT pake flask-jwt-extended
"""

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
SYSTEM_DIR= 'C:/[ DATA (F)]/DemoVenv/flask/DemoUpload'
UPLOAD_FOLDER = '/img' #root_path+'/img'

app = Flask(__name__)
flask_bcrypt = Bcrypt(app)
jwt = JWTManager(app)

app.config['SERVER_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_HOST'] = app.config['SERVER_HOST']
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'myusers'
app.config['UPLOAD_FOLDER'] = SYSTEM_DIR+UPLOAD_FOLDER
app.config['SERVER_URL_HTTP'] = 'http://'+app.config['SERVER_HOST']
app.config['SERVER_URL_HTTPS'] = 'https://'+app.config['SERVER_HOST']
app.config['JWT_SECRET_KEY'] = 'Bagas123'#os.environ.get('SECRET')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
mysql = MySQL(app)


@jwt.unauthorized_loader
def unauthorized_response(callback):
    return jsonify({
        'ok': False,
        'message': 'Missing Authorization Header'
}), 401
 

@app.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    ''' refresh token endpoint '''
    current_user = get_jwt_identity()
    ret = {
        'token': create_access_token(identity=current_user)
    }
    return jsonify({'ok': True, 'data': ret}), 200

@app.route('/mimin/auth', methods=['POST'])
def auth_user():
    ''' auth endpoint '''
    _email   = request.form['email']
    _password = request.form['password']
    if _email and _password:
        user = search_user(_email,_password)
        if len(user)>0 :
            access_token = create_access_token(identity=user["email"])
            refresh_token = create_refresh_token(identity=user["email"])
            user['token'] = access_token
            user['refresh'] = refresh_token
            return jsonify({'ok': True, 'data': user}), 200
        else:
            return jsonify({'ok': False, 'message': 'invalid username or password'}), 401
    else:
        return jsonify({'ok': False, 'message': 'Bad request '}), 400

def search_user(_email,_password):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admin where email = %s and  password = %s",(_email,_password))
    data = cursor.fetchall()
    dataList = []
    if data is not None:
        for item in data:
            dataTempObj = {
                'email'          : item[1],
                'password'         : item[2]
            }
            dataList.append(dataTempObj)
        return dataList[0]
    else:
        return  dataList[0]

# @app.route('/mimin/register', methods=['POST'])
# def register():
#     ''' register user endpoint '''
#     _email   = request.form['email']
#     _password = request.form['password']
#     if _email and _password:
#         data = {}
#         data['password'] = flask_bcrypt.generate_password_hash(_password)
#
#         conn = mysql.connect()
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM admin where email = %s and password = %s ", (_email, _password))
#         conn.commit()
#         if (cursor.rowcount == 0):
#             result = cursor.execute("INSERT INTO admin (email, password) VALUES (%s,%s)", (_email, _password ))
#             conn.commit()
#             conn.close()
#             if (result):
#                 return jsonify({'ok': True, 'data': "Register Admin Success data success!"}), 200  # json.dumps(dataList)
#             else:
#                 return jsonify({'ok': False, 'data': "Register Admin data failed!"}), 500
#         else:
#             conn.close()
#             return jsonify({'ok': False, 'data': "Register Admin data failed! data is exist!"}), 400
#     else:
#         return jsonify({'ok': False, 'data': "Register Admin data failed! please fill the input!"}), 200

@app.route('/user', methods=['GET', 'DELETE', 'PATCH'])
@jwt_required
def user():
    ''' route read user '''
    if request.method == 'GET':
        return jsonify({'ok': True, 'data': ""}), 200
    if request.method == 'DELETE':
        return jsonify({'ok': False, 'message': 'Bad request parameters!'}), 400

# ======================================================= SHOW
@app.route('/user/show',methods=['POST'])
@jwt_required
def show_all(): 
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_profile")
    data = cursor.fetchall()
    dataList = []
    if data is not None:
        for item in data:
            dataTempObj = {
                'id'        : item[0],
                'name'      : item[1],
                'email'     : item[2],
                'ukuran_baju'  : item[3]
            }
            dataList.append(dataTempObj)
        return  jsonify({'ok': True, 'data': dataList}), 200 #json.dumps(dataList)
    else:
        return  jsonify({'ok': False, 'data': "No Data Matches The Selection"}), 204 #json.dumps(dataList)

@app.route('/user/show/<id>',methods=['POST'])
@jwt_required
def show_by_id(id): 
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_profile where id = %s",(int(id)))
    data = cursor.fetchall()
    dataList = []
    if data is not None:
        for item in data:
            dataTempObj = {
                'id'            : item[0],
                'name'          : item[1],
                'email'         : item[2],
                'ukuran_baju'   : item[3]
            }
            dataList.append(dataTempObj)
        return  jsonify({'ok': True, 'data': dataList}), 200 #json.dumps(dataList)
    else:
        return  jsonify({'ok': False, 'data': "No Data Matches The Selection"}), 204 #json.dumps(dataList)


 # ======================================================= INSERT
@app.route('/user/insert',methods=['POST'])
@jwt_required
def insert():
    _name   = request.form['nama']
    _email  = request.form['email']
    _ukuran_baju   = request.form['ukuran_baju']
    # jika user input file untuk ganti
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    filename = file.filename
    if _name and _email and _ukuran_baju and file.filename != '':
        conn = mysql.connect()
        cursor = conn.cursor()
	    # Check if user is exist, if True
        cursor.execute("SELECT * FROM user_profile where nama = %s and email = %s ",(_name,_email))
        conn.commit()
        if (cursor.rowcount == 0 ):
            _img = filename #concatURL(app.config['SERVER_HOST']+UPLOAD_FOLDER,_name+"_"+_email+"." + filename.split(".")[-1])
            upload_img(file)
            result = cursor.execute("INSERT INTO user_profile (nama,email,ukuran_baju,img) VALUES (%s,%s,%s,%s)",(_name,_email,_ukuran_baju,_img))
            conn.commit()
            conn.close()

            if(result):
                return  jsonify({'ok': True, 'data': "Insert data success!"}), 200 #json.dumps(dataList)
            else:
                return  jsonify({'ok': False, 'data': "Insert data failed!"}), 500
        else:
            conn.close()
            return  jsonify({'ok': False, 'data': "Insert data failed! data is exist!"}), 400
    else :
        return  jsonify({'ok': False, 'data': "Insert data failed! please fill the input!"}), 200


 # ======================================================= UPDATE
@app.route('/user/update/<id>',methods=['POST'])
@jwt_required
def update(id):
    # dari DATABASE
    _name   = request.form['nama']
    _email  = request.form['email']
    _ukuran_baju   = request.form['ukuran_baju']
    _img   = request.form['img'] #inputan dari database HIDDEN
    filename = ''
    # jika user input file untuk ganti
    if 'file' in request.files:
        file = request.files['file']
        filename = secure_filename(file.filename)

    if _name and _email and _ukuran_baju and _img:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_profile where id = %s ", int(id))
        data = cursor.fetchall()
        if (cursor.rowcount > 0):
            if filename != '' and check_img(concatPath(data[0][4])):
                # User input file baru & di server ada file yg lama
                delete_img(concatPath(data[0][4]))
                _img = filename #concatURL(app.config['SERVER_HOST']+UPLOAD_FOLDER,str(id)+"_"+_email+"." + filename.split(".")[-1])
                upload_img(file)

            result = cursor.execute("UPDATE user_profile SET nama = %s, email = %s, ukuran_baju = %s, img = %s WHERE id = %s",
                (_name, _email, _ukuran_baju, _img, int(id)))
            conn.commit()
            conn.close()
            if(result):
                return  jsonify({'ok': True, 'data': "Update data success!"}), 200 #json.dumps(dataList)
            else:
                return  jsonify({'ok': False, 'data': "Update data failed!"}), 500
        else:
            conn.close()
            return  jsonify({'ok': False, 'data': "Update data failed! data is not exist!"}), 400
    else :
        return  jsonify({'ok': False, 'data': "Update data failed! please fill the input!"}), 200

 # ======================================================= DELETE
@app.route('/user/delete/<id>',methods=['POST'])
@jwt_required
def delete(id): 
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_profile where id = %s ", int(id))
    data = cursor.fetchall()
    if (cursor.rowcount > 0):
        delete_img(concatPath(data[0][4]))
        result = cursor.execute("DELETE FROM user_profile WHERE id = %s",int(id))
        conn.commit()
        conn.close()
        if(result):
                return  jsonify({'ok': True, 'data': "Delete data success!"}), 200 #json.dumps(dataList)
        else:
                return  jsonify({'ok': False, 'data': "Delete data failed!"}), 500
    else:
        return  jsonify({'ok': False, 'data': "Delete data failed! data is not exist!"}), 400

 # ======================================================= Image Utils
def upload_img(file):
    if file.filename == '':
        # flash('No file selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(concatPath(file.filename))
        # flash('File successfully uploaded')
        return redirect('/')
    else:
        # flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
        return redirect(request.url)
def check_img(filepath):
    return os.path.exists(filepath)
def delete_img(filepath):
    os.remove(filepath)
def concatPath(filename):
    # Path ke storage
    return os.path.join(app.config['UPLOAD_FOLDER'], filename)
def concatURL(url,filename):
    # Path ke URL
    return "http://"+url+"/"+filename
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
	app.run()