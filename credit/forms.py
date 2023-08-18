from django import forms
from django.core.exceptions import ValidationError
from .models import CustomUser

class SignupForm(forms.ModelForm):
    email_conf = forms.EmailField()
    password_conf = forms.CharField()

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        print(email)
        email_confirmation = cleaned_data.get('email_conf')
        print(email_confirmation)
        password = cleaned_data.get('password')
        print(password)
        password_confirmation = cleaned_data.get('password_conf')
        print(password_confirmation)

        if email != email_confirmation:
            raise ValidationError('メールアドレスが一致しません')

        if password != password_confirmation:
            raise ValidationError('パスワードが一致しません')

        return cleaned_data