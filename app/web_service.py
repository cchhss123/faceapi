import face_recognition
from flask import Flask, url_for, jsonify, request, redirect
from flask_restx import Api, Resource, fields
import pickle
import sys
import os
import time
import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
api = Api(app, version='1.0', title='人臉辨識/人臉訓練 API', description='API for 人臉辨識/人臉訓練', doc='/api/')
ns = api.namespace('', description='人臉辨識')  # 設定命名空間為根目錄

result_recog_model = api.model('ResultRecog', {
    'code': fields.Integer(description='0 for success, 1 for error'),
    'personId': fields.String(description='Recognized person ID'),
    'confidence': fields.Float(description='Confidence of recognition'),
    'f': fields.String(description='Input file path'),
    'g': fields.String(description='Group name'),
    'status': fields.String(description='Error message')
})

result_encode_model = api.model('ResultEncode', {
    'code': fields.Integer(description='0 for success, 1 for error'),
    'f': fields.String(description='Input file path'),
    'e': fields.String(description='Encoded file path'),
    'status': fields.String(description='Error message')
})

# 設定檔案上傳目錄
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 允許的檔案類型
# ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_EXTENSIONS = {'jpg'}

# 檢查檔案類型是否允許
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'message': 'File uploaded successfully'}), 200
    else:
        return jsonify({'error': 'Invalid file type'}), 400

#===face_recognition check=================================
@ns.route('/face_recog')
class FaceRecog(Resource):
    @ns.doc('face_recog_post')
    @ns.param('file', 'Image file to check', _in='formData', type='file', required=True)
    @ns.marshal_with(result_recog_model)
    def post(self):
        '''上傳頭像檔案，進行人臉識別'''
        # checkFile = request.values.get('file')
        file = request.files['file']
        group = "test"#request.values.get('group')
        filename = secure_filename(file.filename)
        filename1 = os.path.join('static/temp', filename)
        checkFile = os.path.join('static/temp', "temp") + str(int(time.time())) + ".jpg"
        file.save(filename1)
        os.rename(filename1,checkFile)

        if checkFile is not None and group is not None :
            known_face_encodings = []
            known_person_id = []
            # 取得所有imgencode檔案
            encodefiles = os.listdir("/app/id_encode/" + group)
            # print("encodefiles = " + str(len(encodefiles)))
            for f in encodefiles:
                person_id1 = f
                encodeFile = "/app/id_encode/" + group + "/" + f
                print(encodeFile)
                with open(encodeFile, "rb") as fp:   # Unpickling
                    face_encoding1 = pickle.load(fp)
                    known_face_encodings.append(face_encoding1)
                    known_person_id.append(person_id1)

            unknown_image = face_recognition.load_image_file(checkFile)
            face_encodings = face_recognition.face_encodings(unknown_image)

            if len(face_encodings) < 1 :
                os.remove(checkFile)
                time.sleep(0.01)
                timeend = time.time()
                exit()
            # See if the face is a match for the known face(s)
            # matches = face_recognition.compare_faces(known_face_encodings, face_encodings[0], 0.37)
            distances = face_recognition.face_distance(known_face_encodings, face_encodings[0])
            theIndex = 0
            minVal = 999
            #for idx, val in enumerate(distances):
            lendistances = len(distances)

            #for idx in range(len(distances)):
            idx = 0
            while idx < lendistances:
                val = distances[idx]

                if val < minVal :
                    minVal = val
                    theIndex = idx

                idx = idx + 1

            if minVal < 0.45 :
                #print("theIndex= " + str(theIndex))
                personId = known_person_id[theIndex]
                code = 0
                confidence = 1 - minVal

            else:
                code = 1
                confidence = 1 - minVal
                personId = ""

            return {
                "code": code,
                "personId": personId,
                "confidence": confidence,
                "f": checkFile,
                "g": group
            }
        else:
            return {"code": 1, "status": "parameter error"}, 400

#===face_encode=================================
@ns.route('/face_encode')
class FaceEncode(Resource):
    @ns.doc('face_encode_post')
    @ns.param('name', 'Name of the person', _in='formData', required=True)
    @ns.param('file', 'Image file to encode', _in='formData', type='file', required=True)
    @ns.marshal_with(result_encode_model)
    def post(self):
        '''上傳頭像檔案 與 姓名，進行人臉編碼'''
        # inputFile = request.values.get('file')
        # encodeFile = request.values.get('encode')
        name = request.values.get('name')
        file = request.files['file']
        group = "test"#request.values.get('group')
        filename = secure_filename(file.filename)
        filename1 = os.path.join('static/' + group, filename)
        inputFile = os.path.join('static/' + group, name) + ".jpg"
        encodeFile = os.path.join('id_encode/' + group, name)
        file.save(filename1)
        os.rename(filename1,inputFile)

        if inputFile is not None and encodeFile is not None :
            person_image = face_recognition.load_image_file(inputFile)
            person_encoding = face_recognition.face_encodings(person_image)[0]
            with open(encodeFile , "wb") as fp:
                pickle.dump(person_encoding, fp)

            return {
                "code": 0,
                "f": inputFile,
                "e": encodeFile
            }

        else:
            return {"code": 1, "status": "parameter error"}, 400

#===列出已訓練人臉 / 比對人臉識別=================================
@app.route('/manage', methods=['GET', 'POST'])
def recog_image():
    # Check if a valid image file was uploaded
    htmRecog = ""
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']
        group = request.values.get('group')
        act = request.values.get('act')
        name = request.values.get('name')

        if file.filename == '':
            return redirect(request.url)

        # if file and allowed_file(file.filename):
            # The image file seems valid! Detect faces and return the result.
            # return detect_faces_in_image(file)

        # 訓練人臉
        if act == 'train':
            filename = secure_filename(file.filename)
            filename1 = os.path.join('static/' + group, filename)
            filename2 = os.path.join('static/' + group, name) + ".jpg"
            encodeFile = os.path.join('id_encode/' + group, name)
            file.save(filename1)
            os.rename(filename1,filename2)
            person_image = face_recognition.load_image_file(filename2)
            person_encoding = face_recognition.face_encodings(person_image)[0]
            with open("/app/" + encodeFile , "wb") as fp:
                pickle.dump(person_encoding, fp)

        # 辨識人臉
        if act == 'recog':
            filename = secure_filename(file.filename)
            filename1 = os.path.join('static/temp', filename)
            filename2 = os.path.join('static/temp', "temp") + str(int(time.time())) + ".jpg"
            file.save(filename1)
            os.rename(filename1,filename2)            
            known_face_encodings = []
            known_person_id = []
            # 取得所有imgencode檔案
            encodefiles = os.listdir("/app/id_encode/" + group)
            print("encodefiles = " + str(len(encodefiles)))
            for f in encodefiles:
                person_id1 = f
                encodeFile = "/app/id_encode/" + group + "/" + f
                # print(encodeFile)
                with open(encodeFile, "rb") as fp:   # Unpickling
                    face_encoding1 = pickle.load(fp)
                    known_face_encodings.append(face_encoding1)
                    known_person_id.append(person_id1)

            inputFile = filename2

            unknown_image = face_recognition.load_image_file(inputFile)
            face_encodings = face_recognition.face_encodings(unknown_image)

            if len(face_encodings) < 1 :
                # os.remove(inputFile)
                time.sleep(0.01)
                timeend = time.time()

                #print("invalid-face exec_time: " + str(timeend - timest))#about 0.05 sec
                exit()
            # See if the face is a match for the known face(s)
            distances = face_recognition.face_distance(known_face_encodings, face_encodings[0])
            theIndex = 0
            minVal = 999
            #for idx, val in enumerate(distances):
            lendistances = len(distances)

            #for idx in range(len(distances)):
            idx = 0
            while idx < lendistances:
                val = distances[idx]

                if val < minVal :
                    minVal = val
                    theIndex = idx

                idx = idx + 1

            if minVal < 0.3 :
                personId = known_person_id[theIndex]
                code = 0
                confidence = 1 - minVal

            else:
                code = 1
                confidence = 1 - minVal
                personId = "[無匹配人臉]"

            htmRecog = "<p><table><tr><td>輸入影像</td><td>識別結果</td></tr><tr><td><img width='155px' src='" + inputFile + "' /></td><td style='color:blue;font-weight: bold;'>姓名:" + personId + "<br>信心值:" + str(confidence) + "</td></tr></table></p>"

    # If no valid image file was uploaded, show the file upload form:
    # 取得所有imgencode檔案
    testfiles = os.listdir("/app/static/test/")
    print("testfiles = " + str(len(testfiles)))
    htm1 = ""
    for f in testfiles:
        # fna = url_for('static', filename='andrew3.jpg')
        fna = url_for('static', filename='test/' + f)
        htm2 = '<tr><td><img width="155px" src="' + fna + '" /></td><td>' + f.replace(".jpg", "") + "</td></tr>"
        htm1 = htm1 + htm2

    htm1 = htmRecog + "<p>已訓練人臉一覽表如下</p><table><tr><td><center><b>頭像</b></center></td><td><center><b>姓名</b></center></td></tr>" + htm1 + "</table>"

    htm = """
    <!doctype html>
    <title>人臉識別管理</title>
    <h2>人臉識別 / 人臉訓練 管理頁面</h2>
    <h3>這是人臉識別管理頁面，可以上傳 頭像 進行[人臉訓練]與[人臉識別]</h3>
    <h3>另有提供API呼叫功能，請參閱<a href="/api/">API文件連結</a></h3>
    <form method="POST" enctype="multipart/form-data">
      <input type="hidden" name="act" id="act" value="">
      <input type="hidden" name="group" id="group" value="test">
      <table style="border: 1px;width:500px;"><tr><td>
        人臉檔(.jpg):<input type="file" name="file" id="file">
      </td><td width="30%">
        <input type="button" value="識別 人臉" onclick="if (document.getElementById('file').files.length === 0) {alert('請選擇一個檔案！');return;};if (document.getElementById('file').files[0].name.indexOf('.jpg') == -1) {alert('請選擇.jpg格式檔案！');return;};document.getElementById('act').value='recog';form.submit();">
      </td></tr>
      <tr><td>
        姓名(person-id):<input type="text" name="name" id="name">
      </td><td>
        <input type="button" style="text-align:right;" value="訓練 人臉" onclick="if (document.getElementById('file').files.length === 0) {alert('請選擇一個檔案！');return;};if (document.getElementById('name').value == '') {alert('姓名不可空白');return;};document.getElementById('act').value='train';form.submit();">
      </td></tr>
      </table>
      </div>
    </form>
    <style>
    table, th, td {
      border: 1px solid black;
      border-collapse: collapse;
    }
    </style>
    """

    return htm + htm1


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
