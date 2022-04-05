from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    """
    패스워드는 상속
    """
    class Meta:
        db_table = "accounts_user"
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(
        '유저이름',
        max_length=20,
        help_text='20자 이하로 작성해주세요 @/./+/-/_ 를 사용 할 수 있습니다..',
        unique=True
    )
    email = models.EmailField('이메일')
