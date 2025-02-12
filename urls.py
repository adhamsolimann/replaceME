from django.urls import path
from .import views
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include

urlpatterns=[
    path('',views.index,name="index"),
    path('contacted/',views.contacted,name="contacted"),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('password_change/', auth_views.PasswordChangeView.as_view(),name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(),name='password_change_done'),
    path('preferences/', views.preferenceForm, name="preferences"),
    path('profil/', views.profil, name="profil"),
    path('preferences/table', views.table, name="table"),
    path('warenkorb/', views.warenkorb, name="warenkorb"),
    path('warenkorbAdd/<int:pk>', views.warenkorbAdd_view,name='warenkorbAdd'),
    path('warenkorbRemove/<int:pk>', views.warenkorbRemove_view, name='warenkorbRemove'),
    path('usecase/',views.add_usecase_view, name='usecase'),
    path('about/', views.about, name="about"),
    path('payment', views.payment_view,name='payment'),
    path('orders', views.orders_view,name='orders'),
    path('orderDetails/<int:id>', views.orderDetails_view,name='orderDetails'),
    path('download_view', views.download_view,name='download_view'),
    ]
urlpatterns += staticfiles_urlpatterns()