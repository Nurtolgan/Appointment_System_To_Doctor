from time import timezone

from django import forms
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from users.models import CustomUser
from .models import Post, Comment, Zapis
import datetime as date

class PostForm(forms.ModelForm):
    search_user = forms.CharField(max_length=100, required=False)

    class Meta:
        model = Post
        fields = ['first_name', 'last_name', 'image', 'speciality', 'experience', 'phone', 'email', 'location', 'education', 'procedure', 'user']
        widgets = {
            'user': forms.HiddenInput(),
        }

    user = forms.ModelChoiceField(queryset=CustomUser.objects.all())


class CommentForm(forms.ModelForm):
    name = forms.CharField(label='Ваше имя')
    email = forms.EmailField(label='Почта')
    body = forms.CharField(widget=forms.Textarea, label='Комментарий')

    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['name'].initial = user.username
            self.fields['name'].widget.attrs['readonly'] = True
            self.fields['email'].initial = user.email
            self.fields['email'].widget.attrs['readonly'] = True


class TranslatedCommentForm(forms.ModelForm):
    translated_body = forms.CharField(widget=forms.Textarea, label='Перевод')

    class Meta:
        model = Comment
        fields = ('translated_body',)
        widgets = {
            'translated_body': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }



class AppointmentForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.TextInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Date'
    )
    time_slot = forms.ChoiceField(
        widget=forms.RadioSelect(),
        label='Time Slot',
        choices=(
            ('9:00', '9:00'),
            ('10:00', '10:00'),
            ('11:00', '11:00'),
            ('12:00', '12:00'),
            ('14:00', '14:00'),
            ('15:00', '15:00'),
            ('16:00', '16:00'),
            ('17:00', '17:00'),
        )
    )

    class Meta:
        model = Zapis
        fields = ['date', 'time_slot']

    def clean_date(self):
        selected_date = self.cleaned_data['date']
        selected_datetime = date.datetime.combine(selected_date, date.datetime.min.time())
        if selected_datetime.weekday() == 6:
            raise ValidationError("Appointments are not available on Sundays.")

        return selected_date


