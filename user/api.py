from ninja import Router

from user.models import User

router = Router()


@router.get(path='/')
def get_users(request):
    users = User.objects.all()
    return users
