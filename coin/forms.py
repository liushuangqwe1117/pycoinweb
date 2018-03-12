from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label="用户名", label_suffix="", max_length=64)
    password = forms.CharField(label="密码", label_suffix="", max_length=64, widget=forms.PasswordInput)
