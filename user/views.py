from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from adminapp.models import Poll, Vote, Option

@login_required
def user_home(request):
    polls = Poll.objects.filter(is_active=True)  
    my_votes = Vote.objects.filter(user=request.user).select_related("poll", "option")
    return render(request, "user_home.html", {"polls": polls, "my_votes": my_votes})

@login_required
def vote_poll(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    if request.method == "POST":
        option_id = request.POST.get("option")
        if option_id:
            option = get_object_or_404(Option, id=option_id, poll=poll)
            
            # check if user already voted for this poll
            if Vote.objects.filter(user=request.user, poll=poll).exists():
                messages.error(request, "You have already voted in this poll.")
            else:
                Vote.objects.create(user=request.user, poll=poll, option=option)
                messages.success(request, "Your vote has been recorded.")
        return redirect("user_home")

    return render(request, "vote_poll.html", {"poll": poll})
