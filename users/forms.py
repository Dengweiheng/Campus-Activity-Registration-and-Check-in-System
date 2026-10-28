from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class RegisterForm(UserCreationForm):
    real_name = forms.CharField(label='真实姓名', max_length=50, required=True,
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入真实姓名'}))
    student_id = forms.CharField(label='学号/工号', max_length=20, required=True,
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入学号或工号'}))
    phone = forms.CharField(label='手机号', max_length=20, required=False,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入手机号（选填）'}))
    email = forms.EmailField(label='邮箱', required=False,
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '请输入邮箱（选填）'}))
    role = forms.ChoiceField(
        label='注册身份',
        choices=[('student', '学生'), ('organizer', '活动组织者')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'real_name', 'student_id', 'phone', 'email', 'role', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': '请输入用户名'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': '请输入密码'})
        self.fields['password1'].help_text = ''
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': '请再次输入密码'})
        self.fields['password2'].help_text = ''
        self.fields['username'].label = '用户名'
        self.fields['password1'].label = '密码'
        self.fields['password2'].label = '确认密码'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.real_name = self.cleaned_data['real_name']
        user.student_id = self.cleaned_data['student_id']
        user.phone = self.cleaned_data.get('phone', '')
        user.email = self.cleaned_data.get('email', '')
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('real_name', 'student_id', 'phone', 'email')
        labels = {
            'real_name': '真实姓名',
            'student_id': '学号/工号',
            'phone': '手机号',
            'email': '邮箱',
        }
        widgets = {
            'real_name': forms.TextInput(attrs={'class': 'form-control'}),
            'student_id': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
