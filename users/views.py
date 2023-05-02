from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.models import Group
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from crud.models import Zapis, Post
from . forms import CustomUserCreationForm, CustomUserChangeForm


def home(request):
    return render(request, 'base.html')


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('home')
    template_name = 'users/signup.html'

    def post(self, request, *args, **kwargs):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()


            user_group = Group.objects.get(name=form.cleaned_data['groups'])
            user.groups.add(user_group)

            # Multiple user Groups
            # for form_ug in form.cleaned_data['groups']:
            #     user_group = Group.objects.get(name=form_ug.name)
            #     user.groups.add(user_group)


            logout(request)


            new_user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'],
                                    )
            login(request, new_user)

            return redirect('home')
        else:
            return render(request, self.template_name, {'form' : form })


class LoginView(LoginView):
    template_name = 'users/login.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            #if user's group is 'Доктор' redirect to home page
            if self.request.user.groups.filter(name='Доктор').exists():
                return redirect('logout')
        return self.render_to_response(self.get_context_data())


@login_required
def profile_update(request):
    user = request.user
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = CustomUserChangeForm(instance=user)
    return render(request, 'users/profile.html', {'form': form})


@login_required
def profile_two(request):
    if request.user.groups.filter(name='Доктор').exists():
        doctor_posts = Post.objects.filter(user=request.user)
        appointments = Zapis.objects.filter(post__in=doctor_posts).order_by('date')
        context = {
            'appointments': appointments,
        }
        return render(request, 'users/profile3.html', context=context)
    else:
        user_appointments = Zapis.objects.filter(user=request.user).order_by('date')
        post_info = {}
        for appointment in user_appointments:
            post_info[appointment.post.id] = appointment.post

        context = {
            'appointments': user_appointments,
            'post_info': post_info
        }
        return render(request, 'users/profile2.html', context=context)



