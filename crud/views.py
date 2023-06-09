import datetime
import json
from time import timezone

from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.template.loader import render_to_string
from textblob import TextBlob

from crud.models import Post, CustomUser, Zapis, TranslatedComment
from django.shortcuts import render, get_object_or_404
from users.models import CustomUser
from .forms import PostForm, CommentForm, AppointmentForm, TranslatedCommentForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Avg
from .filters import PostFilter

# Функция для отображения списка врачей и фильтрации по специальности, а также вывода средней оценки
def index(request):
    if request.method == 'GET':
        query = request.GET.get('q')
        #Поиск по специальности
        if query:
            results = Post.objects.filter(Q(last_name__icontains=query) | Q(speciality__icontains=query)).annotate(
                num_comments=Count('comments')).order_by('-experience')
        else:
            results = Post.objects.all().annotate(num_comments=Count('comments')).order_by('-experience')
        #Подсчет средней оценки анкет
        for post in results:
            comments = post.comments.filter(active=True)
            tone_scores = []
            for comment in comments:
                tone_score = comment.sentiment_score
                tone_scores.append(tone_score)
            if tone_scores:
                avg_tone_score = round((sum(tone_scores) / len(tone_scores)) * 5 + 5, 1)
            else:
                avg_tone_score = None
            post.avg_tone_score = avg_tone_score

        results = sorted(results, key=lambda x: x.avg_tone_score or 0, reverse=True)

    posts = Post.objects.all()
    post_filter = PostFilter(request.GET, queryset=posts)

    return render(request, 'crud/index.html', {'results': results,
                                               'filter': post_filter})



def index2(request):
    results = Post.objects.all().annotate(num_comments=Count('comments'))

    for post in results:
        comments = post.comments.filter(active=True)
        tone_scores = []
        for comment in comments:
            tone_score = comment.sentiment_score
            tone_scores.append(tone_score)
        if tone_scores:
            avg_tone_score = round((sum(tone_scores) / len(tone_scores)) * 5 + 5, 1)
        else:
            avg_tone_score = None
        post.avg_tone_score = avg_tone_score

    post_filter = PostFilter(request.GET, queryset=results)

    return render(request, 'crud/index2.html', {'results': results,
                                                'filter': post_filter})

#Функция для создания записи
def create(request):
    if not request.user.is_superuser:
        return redirect('crud/auth')
    form = PostForm()
    if request.GET.get('search_user'):
        search_query = request.GET.get('search_user')
        users = CustomUser.objects.filter(username__icontains=search_query)
        form.fields['user'].queryset = users
    return render(request, 'crud/create.html', {"form": form})


def store(request):
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        image = request.FILES['image']
        speciality = request.POST['speciality']
        experience = request.POST['experience']
        phone = request.POST['phone']
        location = request.POST['location']
        education = request.POST['education']
        procedure = request.POST['procedure']
        email = request.POST['email']
        user_id = request.POST['user']

        if not first_name or not last_name or not speciality or not experience or not phone or not location or not education or not procedure or not email or not user_id:
            return redirect('crud/create')

        CustomUser = get_user_model()
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return redirect('crud/create')

        post = Post(first_name=first_name, last_name=last_name, speciality=speciality, experience=experience,
                    phone=phone, location=location, education=education, procedure=procedure, email=email, user=user,
                    image=image)
        post.save()
        messages.success(request, 'Data Inserted successful')
        return redirect('crud/index')


# def view(request, id):
#     #post = Post.objects.get(id=id)
#     post = get_object_or_404(Post, id=id)
#     comments = post.comments.filter(active=True)
#     new_comment = None
#     tone_scores = []
#     sid = SentimentIntensityAnalyzer()
#     if request.method == 'POST':
#         comment_form = CommentForm(data=request.POST)
#         if comment_form.is_valid():
#             new_comment = comment_form.save(commit=False)
#             new_comment.post = post
#             new_comment.save()
#     else:
#         comment_form = CommentForm()
#     for comment in comments:
#         tone_score = sid.polarity_scores(comment.body)['compound']
#         if tone_score > 0:
#             comment.tone = 'positive'
#         elif tone_score == 0:
#             comment.tone = 'neutral'
#         else:
#             comment.tone = 'negative'
#         tone_scores.append(tone_score)
#     if tone_scores:
#         avg_tone_score = sum(tone_scores) / len(tone_scores)
#         score = round((avg_tone_score + 1) * 5, 1)
#     else:
#         avg_tone_score = None
#         score = None
#
#     return render(request, 'crud/view.html', {"posts": post,
#                                               "comments": comments,
#                                               "new_comment": new_comment,
#                                               "comment_form": comment_form,
#                                               "avg_tone_score": avg_tone_score,
#                                               "score": score})

import googletrans
from googletrans import *


#Функция для просмотра записи, добавления комментария, его перевода, определения тональности и сохранения в БД
def view(request, id):
    post = get_object_or_404(Post, id=id)
    comments = post.comments.filter()
    new_comment = None
    tone_scores = []
    comment_form = CommentForm(user=request.user)
    translator = Translator()
    if request.method == 'POST':
        if not Zapis.objects.filter(post=post, user=request.user).exists():
            messages.warning(request,
                             'Вы не можете оставить отзыв, пока не записались на прием к врачу.')
        else:
            comment_form = CommentForm(data=request.POST, user=request.user)
            #Определение языка комментария
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.post = post
                translated_comment = TranslatedComment()
                try:
                    lang = translator.detect(new_comment.body).lang
                    if lang == 'en':
                        translated_comment.translated_body = new_comment.body
                    else:
                        translated_comment.translated_body = translator.translate(new_comment.body).text
                    print(translated_comment.translated_body)
                    #Определение тональности комментария
                    blob = TextBlob(translated_comment.translated_body)
                    tone_score = blob.sentiment.polarity
                    print(tone_score)
                    if tone_score > 0.3:
                        new_comment.sentiment = 'P'
                        print('P')
                    elif tone_score < -0.2:
                        new_comment.sentiment = 'N'
                        print('N')
                    else:
                        new_comment.sentiment = 'O'
                        print('neutral')
                    new_comment.sentiment_score = tone_score
                except:
                    new_comment.sentiment = 'O'
                    translated_comment.translated_body = new_comment.body
                    new_comment.sentiment_score = 0.0

                new_comment.save()
                translated_comment.comment_id = new_comment.id
                translated_comment.save()
    else:
        comment_form = CommentForm(user=request.user)
    for comment in comments:
        tone_score = comment.sentiment_score
        tone_scores.append(tone_score)
    if tone_scores:
        avg_tone_score = sum(tone_scores) / len(tone_scores)
        score = round((avg_tone_score + 1) * 5, 1)

    else:
        avg_tone_score = None
        score = None

    return render(request, 'crud/view.html', {"posts": post,
                                              "comments": comments,
                                              "new_comment": new_comment,
                                              "comment_form": comment_form,
                                              "avg_tone_score": avg_tone_score,
                                              "score": score})

#Функция для анкеты
@login_required(login_url='/login/')
def delete(request, id):
    if not request.user.is_superuser:
        return redirect('crud/auth')
    if not request.user.is_superuser:
        return redirect('crud/auth')
    Post.objects.get(id=id).delete()
    messages.info(request, 'Data Deleted successful')
    return redirect('crud/index')

#Функция для редактирования анкеты
@login_required(login_url='/login/')
def edit(request, id):
    if not request.user.is_superuser:
        return redirect('crud/auth')
    post = Post.objects.get(id=id)
    return render(request, 'crud/edit.html', {"post": post})

#Функция для изменений анкеты
@login_required(login_url='/login/')
def update(request, id):
    if not request.user.is_superuser:
        return redirect('crud/auth')
    if not request.user.is_superuser:
        return redirect('crud/auth')
    post = get_object_or_404(Post, id=id)
    form = PostForm(request.POST or None, instance=post)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('crud/index')
    context = {
        'form': form,
        'post': post,
    }

    return render(request, 'crud/edit.html', context)

def is_not_doctor(user):
    return not user.groups.filter(name='Доктор').exists()


from datetime import datetime, time
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required

#Функция для записи на прием к врачу
@login_required(login_url='/login/')
@user_passes_test(is_not_doctor, login_url='profile2')
def book_appointment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = AppointmentForm()
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            time_slot_str = form.cleaned_data['time_slot']
            time_slot = datetime.strptime(time_slot_str, '%H:%M').time()

            appointment_datetime = datetime.combine(date, time_slot)
            #Условия для записи на прием
            if appointment_datetime <= datetime.now():
                messages.warning(request, 'Выбранный временной интервал уже прошел. Пожалуйста, выберите другой слот.')

            elif post.user == request.user:
                messages.warning(request, 'Вы не можете записаться на свою же анкету.')

            elif not Zapis.objects.filter(post=post, time_slot=time_slot, date=date).exists():
                appointment = Zapis.objects.create(post=post, user=request.user, time_slot=time_slot, date=date)
                appointment.save()
                messages.success(request, 'Запись успешно назначена.')
                return redirect('profile2')
            else:
                messages.warning(request, 'Этот временной интервал уже забронирован. Пожалуйста, выберите другой слот.')
        else:
            messages.warning(request, 'Нельзя записаться на выходной день.')

    return render(request, 'book_appointment.html', {'post': post, 'form': form})

#Функция для отмены записи на прием к врачу
@login_required
def cancel_appointment(request, appointment_id):
    if not request.user.is_superuser:
        return redirect('crud/auth')
    appointment = get_object_or_404(Zapis, id=appointment_id)

    if appointment.user != request.user and appointment.post.user != request.user:
        messages.warning(request, 'You are not authorized to cancel this appointment.')
        return redirect('profile2')

    if request.method == 'POST':
        appointment.delete()
        messages.success(request, 'Appointment canceled successfully.')
        return redirect('profile2')

    return render(request, 'cancel_appointment.html', {'appointment': appointment})

#Функция для отмены записи от имени врача
@login_required
def reject_selected_appointments(request):
    if not request.user.is_superuser:
        return redirect('crud/auth')
    if request.method == 'POST':
        if 'reject_selected' in request.POST:
            selected_appointments_ids = request.POST.getlist('appointment_id')
            selected_appointments = Zapis.objects.filter(id__in=selected_appointments_ids)
            for appointment in selected_appointments:
                appointment.delete()
    return redirect('profile2')


from datetime import datetime
@login_required
def reject_selected_appointments(request):
    if not request.user.is_superuser:
        return redirect('crud/auth')
    if request.method == 'POST':
        if 'reject_selected' in request.POST:
            selected_appointments_ids = request.POST.getlist('appointment_id')
            selected_appointments = Zapis.objects.filter(id__in=selected_appointments_ids)

            # Проверка времени записи
            current_time = datetime.now().time()
            for appointment in selected_appointments:
                appointment_time = datetime.strptime(appointment.time_slot, '%H:%M').time()
                if appointment.date < datetime.now().date() or (
                        appointment.date == datetime.now().date() and appointment_time <= current_time):
                    # Время записи уже прошло, пропустить отмену
                    continue
                appointment.delete()

            messages.success(request, 'Selected appointments rejected successfully.')
    return redirect('profile2')


from django.contrib.auth.decorators import login_required, user_passes_test

def is_admin(user):
    return user.is_superuser

@login_required(login_url='/login/')
def admin(request):
    if not request.user.is_superuser:
        return redirect('crud/auth')

    query = request.GET.get('q')
    if query:
        posts = Post.objects.filter(
            Q(id__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
    else:
        posts = Post.objects.all()
    return render(request, 'crud/admin.html', {'posts': posts})

@login_required(login_url='/login/')
def auth(request):
    return render(request, 'crud/auth.html')


from .models import Comment

@login_required(login_url='/login/')
def comment_approval(request):
    if not request.user.is_superuser:
        return redirect('crud/auth')
    comments = Comment.objects.order_by('-active', 'created_on')
    if request.method == 'POST':
        comment_id = request.POST.get('comment_id')
        action = request.POST.get('action')
        comment = get_object_or_404(Comment, id=comment_id)
        if action == 'approve':
            comment.active = True
            comment.save()
            return redirect('crud/admin_com')

        if action == 'delete':
            comment.delete()
            return redirect('crud/admin_com')

    return render(request, 'crud/admin_com.html', {'comments': comments})