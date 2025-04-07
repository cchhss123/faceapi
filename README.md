# 佈署 Docker for face-api-server 流程

1. 使用 Dockerfile 建立 "face_recog_andrew" image
 
   docker build -t face_recog_andrew . --no-cache


2. 使用 docker-compose 佈署與啟動 容器

   docker-compose up -d


# 人臉識別 / 人臉訓練 管理頁面

    http://localhost:5020/manage

    1. 列出 已進行 人臉訓練 的 頭像一覽表
    2. 可以上傳 頭像，輸入姓名後，進行[人臉訓練]
    3. 可以上傳 頭像 進行[人臉識別]，會比對 已經訓練的人臉中，找出 信心值最高的 頭像


# 提供API

    API文件: http://localhost:5020/api

    1. http://localhost:5020/face_encode (上傳頭像檔案 與 姓名，進行人臉編碼)


    2. http://localhost:5020/face_recog (上傳頭像檔案，進行人臉識別) 


# 未來應用建議

    1.本專案可以作為[人臉識別的API SERVER]，開發者可規劃自己的應用系統，來呼叫API SERVER，建構完整的應用程式。
    
    2.程式碼中有預留group變數，可進一步依據需要使用group變數，區分不同的群組的人臉識別訓練資料。

    3.如有任何建議或改善方案，歡迎來信討論，cchhss123@hotmail.com




