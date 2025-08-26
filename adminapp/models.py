from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Poll(models.Model):
    question = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_polls")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True) 
    expiry_date = models.DateTimeField(null=True)

    def __str__(self):
        return self.question
    
    def total_votes(self):
        return Vote.objects.filter(option__poll=self).count()
    
    def check_and_update_status(self):
        """Update poll status based on expiry date."""
        if self.expiry_date < timezone.now() and self.is_active:
            self.is_active = False
            self.save(update_fields=["is_active"])
        return self.is_active

    def has_expired(self):
        """Just returns True/False if expired (without saving)."""
        return self.expiry_date < timezone.now()

    def save(self, *args, **kwargs):
        """Ensure is_active is set correctly before saving."""
        if self.expiry_date < timezone.now():
            self.is_active = False
        super().save(*args, **kwargs)


class Option(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text

    def votes_count(self):
        return self.votes.count()


class Vote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="votes")
    option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="votes")
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('poll', 'user')  # ensures one vote per poll per user
