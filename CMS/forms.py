from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserCreateForm(UserCreationForm):
    email = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ("username", "password1", "password2","email")

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class  PaperListForm(forms.BaseForm):
    paper_id = forms.IntegerField(required=True)
    action   = forms.CharField(required=True)

