from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', '学生'),
        ('organizer', '活动组织者'),
        ('admin', '管理员'),
    )
    
    real_name = models.CharField('真实姓名', max_length=50, null=True, blank=True)
    student_id = models.CharField('学号/工号', max_length=20, null=True, blank=True)
    phone = models.CharField('手机号', max_length=20, null=True, blank=True)
    role = models.CharField('角色', max_length=20, choices=ROLE_CHOICES, default='student')
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username
