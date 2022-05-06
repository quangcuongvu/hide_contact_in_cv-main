import os
from flask import Flask, flash, request, redirect, render_template,url_for,send_file,jsonify
from werkzeug.utils import secure_filename
from flask import send_from_directory
from pdf_ocr import *
import json
import urllib.request
import shutil
import certifi
import ssl
import requests
import datetime


app=Flask(__name__)

app.secret_key = "secret key"
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

# Get current path
path = os.getcwd()
# file Upload
UPLOAD_FOLDER =  'static/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed extension you can set your own
ALLOWED_EXTENSIONS = set(['doc','docx', 'pdf', 'png', 'jpg', 'jpeg'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return 'Error page. Use http://103.138.113.107:5000/<int:id> in POST body with keys "files[]". Author: Vũ Quang Cường '


@app.route('/<int:upload_id>', methods=['POST'])
def upload_file_api(upload_id):
    # check if the post request has the file part
    if 'files[]' not in request.files:
        resp = jsonify({'message' : 'No file part in the request'})
        resp.status_code = 400
        return resp

    files = request.files.getlist('files[]')
    errors = {}
    success = False
    folder_file=app.config['UPLOAD_FOLDER']+'uv_'+str(upload_id)
    if not os.path.exists(folder_file):
        os.makedirs(folder_file)
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(filename)
            file.save(os.path.join(folder_file, filename))
            success = True
            input=folder_file+'/'+filename
            output=ocr_image(input)
            return output
        else:
            errors[file.filename] = 'File type is not allowed'

    if success and errors:
        errors['message'] = 'File(s) successfully uploaded'
        resp = jsonify(errors)
        resp.status_code = 500
        return resp
    if success:
        resp = jsonify({'message' : 'Files successfully uploaded'})
        resp.status_code = 201
        return resp
    else:
        resp = jsonify(errors)
        resp.status_code = 500
        return resp


@app.route('/hide_cv', methods=['POST'])
def hide_cv():
    list_result = []
    errors = {'message': 'None'}
    # dataBody
    dataBody = request.json
    file_log = open("log.txt", "w+")
    for data in dataBody:
        try:
            print(data["link"])
            upload_id = data["id"]
            url = data["link"]
            output_file = url.split("/")[-1]
            success = False
            folder_file = app.config['UPLOAD_FOLDER'] + 'uv_' + str(upload_id)
            if not os.path.exists(folder_file):
                os.makedirs(folder_file)
            with urllib.request.urlopen(url, cafile=certifi.where()) as response, open(output_file, 'wb') as out_file:
                size=response.length
                if size<5000000:
                    shutil.copyfileobj(response, out_file)
                else:
                    print('file too big')
                    os.unlink(out_file)

            shutil.move(output_file, folder_file + '/' + output_file)
            if output_file and allowed_file(output_file):
                filename = secure_filename(output_file)
                is_exits = os.path.exists(folder_file + '/' + filename)
                print(filename + "isExit: " + str(is_exits))
                if is_exits is False:
                    file_log.write(str(datetime.datetime.now()) + ": File not exits id: {}, link: {}\r\n".format(upload_id, url))
                    continue
                success = True
                input = folder_file + '/' + filename
                try:
                    output = ocr_image(input)
                except print(0):
                    file_log.write(str(datetime.datetime.now()) + ": Can't pase file: {}, link: {}\r\n".format(upload_id, url))
                    continue
                item = {
                    "id": upload_id,
                    "link": output
                }
                list_result.append(item)
                # return output
            else:
                errors[output_file] = 'File type is not allowed'
        except Exception:
            print("An exception occurred")
            pass
            continue

    return jsonify(list_result)
    # return listData[0]["link"]

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)