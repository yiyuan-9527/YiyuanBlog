from ninja import NinjaAPI

api = NinjaAPI(
    title='YiyuanBlog API',
    version='0.0.1',
    description='這是一個 YiyuanBlog 的 API 文件, 供讀者參考',
)

# User API
api.add_router(prefix='', router='user.api.router', tags=['User'])
