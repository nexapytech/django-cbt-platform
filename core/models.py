from django.db import models
from django.contrib.auth.models import AbstractUser,  Permission
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
import uuid
import hashlib
from django.utils import  timezone
from django.utils.timezone import now, timedelta
from django.db.models.signals import post_save




User = get_user_model()

GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
    ('prefer_not_to_say', 'Prefer not to say'),
]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    exams_created = models.IntegerField(default=0)

    preferences = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.user.username

class Email_Verification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=200, default=uuid.uuid4, editable=False)
    full_token = models.CharField(max_length=500, blank=True,  editable=False)
    make_token = models.CharField(max_length=500, blank=True,  editable=False)
    timestamp = models.DateTimeField(max_length=100, default=timezone.now)
    is_email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, unique=True)
    browser_info = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

class Exam(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=True)
    title = models.CharField(max_length=255, default="Untitled Exam")
    description = models.TextField(blank=True)
    questions_data = models.JSONField(blank=True, default=list)  # Store JSON data
    is_published = models.BooleanField(default=False)
    published_hash = models.CharField(max_length=100, unique=True, blank=True, null=True)
    published_url= models.URLField(unique=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_published_hash(self):
        """
        This method generates a unique hash for the published exam
        using the UUID and title (or a default string if no title).
        """
        # Combine UUID and title for hashing
        unique_string = f"{self.user}{self.uuid}{self.title}"
        return hashlib.sha256(unique_string.encode()).hexdigest()[:30]

    def save(self, *args, **kwargs):
        # If this is the first save and the exam is published, generate the hash
        if self.is_published and not self.published_hash:
            self.published_hash = self.generate_published_hash()

        super().save(*args, **kwargs)
    def __str__(self):
        return f'{self.user} | {self.title} | {self.is_published}'
class ExamAnswer(models.Model):
    user = models.ForeignKey(User,   on_delete=models.CASCADE)
    candidate_id = models.CharField(max_length=500, blank=True)
    is_candidate_logined = models.BooleanField(default=False)
    end_exam = models.BooleanField(default=False)
    client_token = models.CharField(max_length=100 , blank=True)
    # Link to user taking the exam
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='candidate_responses')
    score = models.FloatField(default=0, )  # Score after marking
    percentage = models.IntegerField(default=0)
    feedback = models.TextField(default='No feedback')
    exam_status = models.BooleanField(default=False)
    status = models.BooleanField(default='False')
    is_marked = models.BooleanField(default=False)
    answers_data = models.JSONField(default=list, blank=True)  # Store JSON answers
    submitted_at = models.DateTimeField(auto_now_add=True)  # Timestamp when submitted

    def __str__(self):
        return f"Answer by {self.candidate_id} for Exam {self.exam}"


class Question(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    title = models.CharField(max_length=255)
    question_type = models.CharField(
        max_length=50,
        choices=[
            ('short-answer', 'SHORT ANSWER'),
            ('paragraph', 'PARAGRAPH'),
            ('multiple-choice', 'MULTIPLE CHOICE'),
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.title} | {self.question_type}'


class MultipleChoiceOption(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    options = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    answer = models.CharField(max_length=255)
    def __str__(self):
        return f'{self.answer} | {self.options} '
class ExamSetting(models.Model):
    METHOD_CHOICES = [
        ('reg-no', 'Reg-No'),
        ('email', 'Email'),
        ('surname', 'Surname'),
    ]  #
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='settings' )
    countdown_time = models.PositiveIntegerField(help_text="Countdown time in minutes", default=10)
    shuffle_questions = models.BooleanField(
        default=False,
        help_text="Enable to shuffle questions during the exam"
    )  # Toggle button for shuffling questions
    enable_browser_lock = models.BooleanField(
        default=True,
        help_text="Enable to lock the browser during the exam"
    )  # Browser lock toggle
    enable_feedback = models.BooleanField(
        default=False,
        help_text="Enable to provide feedback after the exam"
    )  # Enable feedback toggle
    select_method = models.CharField(
        max_length=50,
        choices=METHOD_CHOICES,
        help_text="Select the method for conducting the exam"
    )  # Dropdown to select method
    uploaded_file = models.FileField(
        upload_to='candidate_files/',
        blank=True,
        null=True,
        help_text="Upload a file related to exam settings"
    )  # File upload field

    def __str__(self):
        return f"Settings for {self.exam.user} | {self.exam.uuid}"