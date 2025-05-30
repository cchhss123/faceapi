# 說明

    1.本專案引用 python face_recognition 套件，以python開發人臉辨識相關應用邏輯，
    並整合 flask 與 flask_restx，建立 RESTful API，產生 Swagger API文件, 開發出[人臉識別API應用服務(face-api-server)]。
    主要功能如下:
    
        1.1.可對 上傳頭像 進行人臉訓練](產生人臉特徵編碼檔)，並將[人臉特徵編碼檔]存放於群組目錄，以提供人臉比對識別。

        1.2.可 上傳頭像，比對[群組目錄]中，在已經訓練的[人臉特徵編碼檔]列表中，找出 信心值最高的 人臉頭像。

    2.感謝 face_recognition 套件的作者 Adam Geitgey，讓其他開發者能夠輕鬆地實現人臉辨識功能。
    face_recognition 套件，將 dlib 的人臉辨識功能進行了 Python 封裝，使其更易於使用。
    face_recognition 官方代碼倉庫: https://github.com/ageitgey/face_recognition


# 以 Docker 佈署 face-api-server 流程

    1. 使用 Dockerfile 建立 "face_recog" image
 
        docker build -t face_recog . --no-cache

    2. 使用 docker-compose 佈署與啟動 專案程式運行容器

        docker-compose up -d


# 人臉識別 / 人臉訓練 管理頁面說明

    管理頁面: http://localhost:5020/manage

    1. 列出 已完成[人臉訓練](產生人臉特徵編碼檔) 的 頭像一覽表

    2. 可以上傳 頭像，輸入姓名後，進行[人臉訓練]，產生人臉特徵編碼檔，存放於群組目錄。
    
    3. 可以上傳 頭像 進行[人臉識別]，比對[群組目錄]中，在已經訓練的[人臉特徵編碼檔]列表中，找出最接近的人臉頭像(找出信心值最高的頭像)。


# 提供 API

    Swagger API 文件 : http://localhost:5020/api

    1. http://localhost:5020/face_encode (上傳頭像檔案 與 姓名，進行人臉編碼)

    2. http://localhost:5020/face_recog (上傳頭像檔案，進行人臉識別) 


# 未來應用建議

    1.本專案可以作為[人臉識別的API SERVER]，開發者可規劃自己的應用系統，來呼叫API SERVER，建構完整的應用程式。
    
    2.程式碼中有預留group變數，可進一步依據需要使用group變數，區分不同的群組的人臉識別訓練資料。

    3.如有任何建議或改善方案，歡迎來信討論，cchhss123@hotmail.com。




