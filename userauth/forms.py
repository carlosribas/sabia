from django import forms
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from .models import CustomUser, USER_TYPE
from wagtail.users.forms import UserCreationForm, UserEditForm


class WagtailUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser


class WagtailUserEditForm(UserEditForm):
    class Meta(UserEditForm.Meta):
        model = CustomUser


class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=100, label=_("First name"))
    last_name = forms.CharField(max_length=100, label=_("Last name"))
    academic_background = forms.ChoiceField(choices=USER_TYPE, label=_("Academic background"))
    other = forms.CharField(max_length=100, label=_("Other"), required="")

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.academic_background = self.cleaned_data['academic_background']
        user.other = self.cleaned_data['other']
        user.save()


class CustomUserUpdateForm(ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone', 'academic_background', 'other', 'certificate']
