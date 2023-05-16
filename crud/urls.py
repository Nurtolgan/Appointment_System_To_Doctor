from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('index/', views.index, name='crud/index'),
    path('index2/', views.index2, name='crud/index2'),
    path('create/', views.create, name='crud/create'),
    path('/store', views.store, name='crud/store'),
    path('/view/<int:id>', views.view, name='crud/view'),
    path('/delete/<int:id>', views.delete, name='crud/delete'),
    path('/edit/<int:id>', views.edit, name='crud/edit'),
    path('/update/<int:id>', views.update, name='crud/update'),

    path('book_appointment/<int:post_id>/', views.book_appointment, name='book_appointment'),
    path('appointments/<int:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('profile2/reject_selected/', views.reject_selected_appointments, name='reject_selected_appointments'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
