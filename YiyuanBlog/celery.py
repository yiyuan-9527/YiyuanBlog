import os

from celery import Celery
from celery.schedules import crontab

# 設定 Django 的環境變數, 如果環境變數 'DJANGO_SETTINGS_MODULE' 尚未設定,
# 則預設為 'YiyuanBlog.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'YiyuanBlog.settings')

app = Celery('YiyuanBlog')
# 抓取所有以 CELERY_ 為前綴的 Django settings 設定
app.config_from_object('django.conf:settings', namespace='CELERY')
# 自動發現所有 Django app 中的 tasks.py 檔案
app.autodiscover_tasks()


@app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    """
    設定定時任務
    """
    from storage.tasks import leetest

    sender.add_periodic_task(
        crontab(minute='*/1'),  # 每分鐘執行一次
        leetest.s(),  # 執行的任務
        name='李白測試',  # 任務名稱
    )
