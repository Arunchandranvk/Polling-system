from django.urls import path
from .views import user_home,vote_poll

urlpatterns = [
    path('user-home', user_home, name='user_home'),
    path('my-votes/<int:poll_id>/', vote_poll, name='vote_poll'),
]
