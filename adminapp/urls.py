from django.urls import path
from .views import LoginView,register,logout_view,poll_add,admin_home,poll_results,all_polls_results,export_polls_results_csv

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("register/", register, name="register"),
    path("admin-home/", admin_home, name="admin_home"),
    path("poll-add/", poll_add, name="poll_add"),
    path("poll-results/<int:poll_id>/", poll_results, name="poll_results"),
    path("polls/results/",all_polls_results, name="all_polls_results"),
path("polls/export/csv/", export_polls_results_csv, name="export_polls_results_csv"),

]
