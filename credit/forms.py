from django import forms
from django.core.exceptions import ValidationError
from .models import CustomUser, Profile, Post, Evidence

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
        email_confirmation = cleaned_data.get('email_conf')
        password = cleaned_data.get('password')
        password_confirmation = cleaned_data.get('password_conf')

        if email != email_confirmation:
            raise ValidationError('メールアドレスが一致しません')

        if password != password_confirmation:
            raise ValidationError('パスワードが一致しません')

        return cleaned_data

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['username', 'backimage', 'image', 'content']

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['period', 'image', 'content']

class EvidenceForm(forms.ModelForm):
    class Meta:
        model = Evidence
        fields = ['text']

    images = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    def clean_images(self):
        images = self.files.getlist('images')
        if len(images) > 4:
            raise ValidationError('画像の上限は4枚です')
        return images
