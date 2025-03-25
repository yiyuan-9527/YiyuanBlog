from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '71f6908acddad0c2063d08af6ed86564e6e1ef98d5601e859d4820dc0e649cd85a4aeb406cac21018aa8cbfb9673bd962f491cf8ea41cc72e19fbd791be9de2e13dac16d1134a8c15781a9f6b79abbd5dca821d0dd34287492ea56da3b28cfc0027476353cd34ae9db449d84243f1fb12768b79cee7a6d46bd8dc58b6c3de6a52d649937c9336fd50ce4c8bd349d68f03fe99ea9ee1ca790e4baf238e3f14fce743b79df381eee8bbd80d40e8534d2055c2d3c4a0ecd4f3eb7b1ec9ab612ff40bcd2326f8d575a0e92111b1f12fa7704b8c5631630e0e4e7e383aba97f7d7752eb3c749e8f5968ca3459b9b30a0e87caaa65d5449a28d573dc90c0e870efd0d9'

# JWT setting
# NINJA_JWT = {
#     'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),  # Access token 過期時間
#     'REFRESH_TOKEN_LIFETIME': timedelta(days=7),  # Regresh token 過期時間
#     'SIGNING_KEY': SECRET_KEY,  # 使用 SECRET_KEY 來簽署 JWT
#     'AUTH_HEADER_TYPES': ('Bearer',),  # 使用 `Bearer` 作為 JWT 標頭
# }

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# 允許所有外部 IP 訪問
ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'user',
    'post',
]

# !重要 不使用內建的 auth.User, 要在第一次 migrate 前使用
AUTH_USER_MODEL = 'user.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'YiyuanBlog.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'YiyuanBlog.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'blog',
        'USER': 'yiyuan',
        'PASSWORD': 'yyb13190303',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 定義媒體檔案的 URL 路徑, 當使用者上傳檔案時, Django 會透過此 URL 存取它們
MEDIA_URL = '/media/'

# 定義伺服器端儲存媒體檔案的實際路徑, 所有上傳的媒體檔案將會儲存在該資料夾內
MEDIA_ROOT = BASE_DIR / 'media'

# CORS 設定, 跨域連結
CORS_ALLOW_ALL_ORIGINS = True
