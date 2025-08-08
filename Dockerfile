# 使用官方 Python, 從 Docker Hub 下載
FROM python:3.12

# 設定容器內的工作目錄 (之後 COPY, RUN, CMD 都會在這裡執行)
WORKDIR /app

# 複製 requirements.txt 到容器內, (先複製是為了加快快取)
COPY requirement.txt /app/

# 安裝 Python 套件 (不使用快取, 避免 pip 舊快取汙染)
RUN pip install --no-cache-dir -r requirements.txt

# 複製整個專案到容器內
COPY . /app/

# 對外開放 8000 port
EXPOSE 8000

# 啟動指令 (開發模式用 runserver)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]