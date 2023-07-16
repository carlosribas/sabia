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
    cpf = forms.CharField(max_length=15, label=_("CPF"))

    def clean_cpf(self):
        cpf = self.cleaned_data['cpf']
        cpf_number = [int(digit) for digit in cpf if digit.isdigit()]
        if len(cpf_number) != 11:
            raise forms.ValidationError(_("Invalid CPF"))
        sop = sum(a * b for a, b in zip(cpf_number[0:9], range(10, 1, -1)))
        ed1 = (sop * 10 % 11) % 10
        sop = sum(a * b for a, b in zip(cpf_number[0:10], range(11, 1, -1)))
        ed2 = (sop * 10 % 11) % 10
        if ed1 != cpf_number[9] or ed2 != cpf_number[10]:
            raise forms.ValidationError(_("Invalid CPF"))
        else:
            result = ''.join(str(d) for d in cpf_number)
            return f'{result[0:3]}.{result[3:6]}.{result[6:9]}-{result[9:]}'

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.academic_background = self.cleaned_data['academic_background']
        user.other = self.cleaned_data['other']
        user.cpf = self.clean_cpf()
        user.save()


class CustomUserUpdateForm(ModelForm):
    # TODO: DRY!
    def clean_cpf(self):
        cpf = self.cleaned_data['cpf']
        cpf_number = [int(digit) for digit in cpf if digit.isdigit()]
        if len(cpf_number) != 11:
            raise forms.ValidationError(_("Invalid CPF"))
        sop = sum(a * b for a, b in zip(cpf_number[0:9], range(10, 1, -1)))
        ed1 = (sop * 10 % 11) % 10
        sop = sum(a * b for a, b in zip(cpf_number[0:10], range(11, 1, -1)))
        ed2 = (sop * 10 % 11) % 10
        if ed1 != cpf_number[9] or ed2 != cpf_number[10]:
            raise forms.ValidationError(_("Invalid CPF"))
        else:
            result = ''.join(str(d) for d in cpf_number)
            return f'{result[0:3]}.{result[3:6]}.{result[6:9]}-{result[9:]}'

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'academic_background', 'other', 'cpf']
