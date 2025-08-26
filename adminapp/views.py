from django.views.generic import FormView,TemplateView
from django.contrib.auth import authenticate, login,logout
from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required,user_passes_test
from django.utils import timezone

from .forms import LoginForm,RegistrationForm
from .models import Poll,Option,Vote
from django.contrib.auth import logout as auth_logout
import datetime
# Create your views here.

def is_admin(user):
    return user.is_superuser 


class LoginView(FormView):
    template_name = "auth/login.html"
    form_class = LoginForm
    success_url = reverse_lazy("user_home")  

    def form_valid(self, form):
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]

        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            login(self.request, user)
            messages.success(self.request, f"Welcome back {user.username}!")

            # Redirect based on user role
            if user.is_superuser or user.is_staff:
                return redirect("admin_home")
            else:
                return redirect("user_home")
        else:
            messages.error(self.request, "Invalid username or password")
            return self.form_invalid(form)
        
        
def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"]
            )
            messages.success(request, "Account created successfully! Please login.")
            return redirect("login")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegistrationForm()
    return render(request, "auth/register.html", {"form": form})

    
@login_required
@user_passes_test(is_admin)
def admin_home(request):
    total_polls = Poll.objects.count()
    total_votes = Vote.objects.count()
    active_polls = Poll.objects.filter(is_active=True).count()  # if you have is_active field
    engagement_rate = 0  

    # Example engagement rate: (votes / polls) * 100 (avoid division by zero)
    if total_polls > 0:
        engagement_rate = round((total_votes / total_polls) * 10)  # customize formula

    context = {
        "total_polls": total_polls,
        "total_votes": total_votes,
        "active_polls": active_polls,
        "engagement_rate": engagement_rate,
    }
    return render(request, "admin_home.html", context)





@login_required
@user_passes_test(is_admin)
def poll_add(request):
    if request.method == "POST":
        question = request.POST.get("question")
        options = request.POST.getlist("options")
        expiry_date = request.POST.get("expiry_date")

        if not question:
            messages.error(request, "Please enter a question.")
            return render(request, "poll_add.html")

        if not options or all(opt.strip() == "" for opt in options):
            messages.error(request, "Please enter at least one valid option.")
            return render(request, "poll_add.html")

        if not expiry_date:
            messages.error(request, "Please select an expiry date.")
            return render(request, "poll_add.html")

        try:
            # Parse string to datetime
            parsed_date = datetime.datetime.fromisoformat(expiry_date)

            # Make timezone aware
            if timezone.is_naive(parsed_date):
                expiry_date = timezone.make_aware(parsed_date)
            else:
                expiry_date = parsed_date
        except ValueError:
            messages.error(request, "Invalid date format.")
            return render(request, "poll_add.html")

        # Create poll
        poll = Poll.objects.create(
            question=question,
            created_by=request.user,
            expiry_date=expiry_date,
            is_active=True if expiry_date > timezone.now() else False,
        )

        # Create options
        for opt in options:
            if opt.strip():
                Option.objects.create(poll=poll, text=opt.strip())

        messages.success(request, "Poll created successfully!")
        return redirect("all_polls_results")

    return render(request, "poll_add.html")





@login_required
@user_passes_test(is_admin)
def poll_results(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    options = poll.options.all()

    total_votes = poll.total_votes()
    data = []
    for option in options:
        count = option.votes.count()
        percentage = (count / total_votes) * 100 if total_votes > 0 else 0
        data.append({
            "text": option.text,
            "count": count,
            "percentage": round(percentage, 2)
        })

    context = {
        "poll": poll,
        "data": data,
        "total_votes": total_votes
    }
    return render(request, "poll_results.html", context)



@login_required
@user_passes_test(is_admin)
def all_polls_results(request):
    polls = Poll.objects.all()

    polls_data = []
    for poll in polls:
        total_votes = poll.total_votes()
        options_data = []
        for option in poll.options.all():
            count = option.votes.count()
            percentage = (count / total_votes) * 100 if total_votes > 0 else 0
            options_data.append({
                "text": option.text,
                "count": count,
                "percentage": round(percentage, 2)
            })

        polls_data.append({
            "poll": poll,
            "total_votes": total_votes,
            "options": options_data
        })

    return render(request, "all_poll_results.html", {"polls_data": polls_data})
    
def logout_view(request):
    auth_logout(request)  
    return redirect('login')


import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test

@login_required
@user_passes_test(is_admin)
def export_polls_results_csv(request):
    # Create HTTP response with CSV content type
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="polls_results.csv"'

    writer = csv.writer(response)
    writer.writerow(["Poll Question", "Option", "Votes", "Percentage", "Created At", "Is Active"])  # CSV header

    polls = Poll.objects.all()

    for poll in polls:
        total_votes = poll.total_votes()
        for option in poll.options.all():
            count = option.votes.count()
            percentage = (count / total_votes * 100) if total_votes > 0 else 0
            writer.writerow([
                poll.question,
                option.text,
                count,
                f"{round(percentage, 2)}%",
                poll.created_at.strftime("%Y-%m-%d %H:%M"),
                "Active" if poll.is_active else "Expired"
            ])

    return response
