from django.contrib import admin
from .models import (UserProfile, Email_Verification, UserSession, UserProfile,ExamSetting,ExamAnswer,
                     Question, MultipleChoiceOption,Exam)
admin.site.site_header = "NEXA CBT HUB ADMIN"
admin.site.site_title = "NEXA CBT  CONTROL PANEL"
admin.site.index_title = "Welcome to the Admin Interface"


# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Email_Verification)
admin.site.register(Exam)
admin.site.register(Question)
admin.site.register(MultipleChoiceOption)
admin.site.register(ExamSetting)
admin.site.register(ExamAnswer)



