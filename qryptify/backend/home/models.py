from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator

class User(AbstractUser):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("researcher", "Researcher"),
        ("guest", "Guest"),
        ("auditor", "Auditor"),
    ]
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default="guest")
    phone = models.CharField(max_length=15, blank=True, null=True)
    limit = models.CharField(
        blank=True, null=True,
        max_length=15
    )

    def __str__(self):
        return f"{self.username} ({self.role})"


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('VIEW_USER','View_User'),
        ('VIEW_LOGS','View_Logs'),
        ('UPLOAD_FILE','Upload_File')
    ]
    actor=models.ForeignKey(User,related_name='performed_actions',on_delete=models.SET_NULL,null=True)
    target_user=models.ForeignKey(User,related_name='affected_by',on_delete=models.SET_NULL,null=True, blank=True)
    action=models.CharField(max_length=20,choices=ACTION_CHOICES)
    message=models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.message


class UsageLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    file_hash = models.CharField(max_length=256)
    algorithm_name = models.CharField(max_length=100)
    confidence_score = models.FloatField()

    usage_timestamp = models.DateTimeField(auto_now_add=True)

    blockchain_hash = models.CharField(max_length=256, null=True, blank=True)
    transaction_hash = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.algorithm_name}"
    
