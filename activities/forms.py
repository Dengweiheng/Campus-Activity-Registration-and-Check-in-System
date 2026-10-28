from django import forms
from .models import Activity


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['title', 'description', 'cover', 'location', 'start_time', 'end_time', 'reg_deadline', 'max_participants', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入活动标题'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': '请输入活动描述（选填）', 'rows': 5}),
            'cover': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入活动地点'}),
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'reg_deadline': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'max_participants': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': '活动标题',
            'description': '活动描述',
            'cover': '活动封面图片',
            'location': '活动地点',
            'start_time': '开始时间',
            'end_time': '结束时间',
            'reg_deadline': '报名截止时间',
            'max_participants': '最大报名人数',
            'status': '活动状态',
        }
