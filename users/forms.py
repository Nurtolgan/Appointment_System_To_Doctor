from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django.contrib.auth.models import Group
import datetime


class CustomUserCreationForm(UserCreationForm):
    groups = forms.ModelChoiceField(queryset=Group.objects.all())

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'gender', 'birth_date', 'phone', 'groups', 'email')
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'phone': forms.TextInput(attrs={'type': 'tel', 'pattern': '[0-9]{11}', 'placeholder': '87xx-xxx-xx-xx',}),
            'gender': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Выберите пол', 'width': '90%'}),
            'groups': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Выберите группу', }),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit():
            raise forms.ValidationError('Телефонный номер должен состоять только из цифр')
        if len(phone) != 11:
            raise forms.ValidationError('Телефонный номер должен состоять из 11 цифр')
        return phone


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'gender', 'birth_date', 'phone', 'groups', 'email')