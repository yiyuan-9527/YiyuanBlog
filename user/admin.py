from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User  # 自定義的 User model

# 讓 User 顯示在 Django Admin 後台
admin.site.register(User, UserAdmin)
