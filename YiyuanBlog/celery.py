import os

from celery import Celery

# 設定 Django 的環境變數, 如果環境變數 'DJANGO_SETTINGS_MODULE' 尚未設定,
# 則預設為 'YiyuanBlog.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'YiyuanBlog.settings')

app = Celery('YiyuanBlog')
# 抓取所有以 CELERY_ 為前綴的 Django settings 設定
app.config_from_object('django.conf:settings', namespace='CELERY')
# 自動發現所有 Django app 中的 tasks.py 檔案
app.autodiscover_tasks()
