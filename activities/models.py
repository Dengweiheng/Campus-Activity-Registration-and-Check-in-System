import uuid
from django.db import models
from django.conf import settings


class Activity(models.Model):
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('published', '已发布'),
        ('ongoing', '进行中'),
        ('finished', '已结束'),
        ('cancelled', '已取消'),
    )

    title = models.CharField('活动标题', max_length=255)
    description = models.TextField('活动描述', blank=True, null=True)
    location = models.CharField('活动地点', max_length=255)
    start_time = models.DateTimeField('开始时间')
    end_time = models.DateTimeField('结束时间')
    reg_deadline = models.DateTimeField('报名截止时间')
    max_participants = models.PositiveIntegerField('最大人数限制', default=0, help_text='0表示不限制人数')
    current_participants = models.PositiveIntegerField('当前报名人数', default=0)
    cover = models.ImageField('活动封面', upload_to='uploads/', blank=True, null=True)
    qr_code = models.ImageField('签到二维码', upload_to='qrcodes/', blank=True, null=True)
    # Unique token embedded in the QR code to prevent forgery
    qr_token = models.UUIDField('二维码令牌', default=uuid.uuid4, unique=True, editable=False)
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='发布者',
        related_name='organized_activities'
    )
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '活动'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_registered_count(self):
        return self.registrations.filter(status='registered').count()

    def get_checkin_count(self):
        return CheckIn.objects.filter(registration__activity=self).count()


class Registration(models.Model):
    STATUS_CHOICES = (
        ('registered', '已报名'),
        ('cancelled', '已取消'),
    )

    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        verbose_name='活动',
        related_name='registrations'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='用户',
        related_name='registrations'
    )
    registration_time = models.DateTimeField('报名时间', auto_now_add=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='registered')

    class Meta:
        verbose_name = '报名记录'
        verbose_name_plural = verbose_name
        unique_together = ('activity', 'user')

    def __str__(self):
        return f"{self.user.username} 报名了 {self.activity.title}"


class CheckIn(models.Model):
    STATUS_CHOICES = (
        ('normal', '正常签到'),
        ('late', '迟到'),
    )

    registration = models.OneToOneField(
        Registration,
        on_delete=models.CASCADE,
        verbose_name='报名记录',
        related_name='checkin'
    )
    check_in_time = models.DateTimeField('签到时间', auto_now_add=True)
    status = models.CharField('签到状态', max_length=20, choices=STATUS_CHOICES, default='normal')
    ip_address = models.GenericIPAddressField('签到IP', null=True, blank=True)
    device_info = models.CharField('设备信息', max_length=512, blank=True, null=True)

    class Meta:
        verbose_name = '签到记录'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.registration.user.username} 签到 {self.registration.activity.title}"
