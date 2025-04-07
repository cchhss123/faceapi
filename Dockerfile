FROM animcogn/face_recognition:cpu

RUN pip3 install --upgrade pip
RUN pip3 install requests
RUN pip3 install flask
RUN pip3 install flask-restx

EXPOSE 5000
