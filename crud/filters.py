from django.contrib.auth.models import User
import django_filters
from .models import Post


class PostFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(lookup_expr='icontains')
    last_name = django_filters.CharFilter(lookup_expr='icontains')
    speciality = django_filters.ModelChoiceFilter(queryset=Post.objects.values_list('speciality', flat=True).distinct())
    min_experience = django_filters.NumberFilter(field_name='experience', lookup_expr='gte')

    class Meta:
        model = Post
        fields = ['first_name', 'last_name', 'speciality', 'min_experience']




