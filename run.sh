#!/bin/bash
# 此腳本的目的是簡化開發環境的啟動流程

echo "--- 啟動 Docker Compose 服務 ---"
# 使用 --build 參數，確保在啟動前重新建立映像檔
# 使用 -d 參數，讓容器在背景執行
docker-compose up --build -d

echo