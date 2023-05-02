from django.contrib import admin
from .models import Post, Comment, Zapis, TranslatedComment
from django.contrib.auth.models import Group
# Register your models here.

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    model = Post
    list_display = ('first_name', 'last_name', 'speciality', 'experience', 'phone', 'location', 'education', 'procedure', 'email', 'user')
    list_filter = ('first_name', 'last_name', 'speciality', 'experience', 'phone', 'location', 'education', 'procedure', 'email')
    search_fields = ('first_name', 'last_name', 'speciality', 'experience', 'phone', 'location', 'education', 'procedure', 'email', 'user__username')

    raw_id_fields = ('user',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            group = Group.objects.get(name='Доктор')
            kwargs['queryset'] = group.user_set.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'body', 'post', 'created_on', 'active')
    list_filter = ('active', 'created_on')
    search_fields = ('name', 'email', 'body')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(active=True)


@admin.register(Zapis)
class ZapisAdmin(admin.ModelAdmin):
    list_display = ('date', 'time_slot', 'post', 'user')
    list_filter = ('date', 'time_slot', 'post', 'user')
    search_fields = ('date', 'time_slot', 'post', 'user')

    raw_id_fields = ('user', 'post')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            group = Group.objects.get(name='Пациент')
            kwargs['queryset'] = group.user_set.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(TranslatedComment)
class TranslatedCommentAdmin(admin.ModelAdmin):
    list_display = ('comment', 'translated_body')
    list_filter = ('comment', 'translated_body')
    search_fields = ('comment', 'translated_body')



