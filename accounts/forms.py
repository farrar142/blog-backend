from django import forms
from django.contrib.auth.forms import UserCreationForm

from accounts.models import User

class UserSignInForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','password']
        
class UserSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['email','username','password1','password2']
        
class IdfinderForm(forms.ModelForm):
    class Meta:
        model = User  # 사용할 모델
        fields = ['email']