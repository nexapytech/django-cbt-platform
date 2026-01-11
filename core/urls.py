from django.urls import path
from . import  views


urlpatterns = [
    path('', views.index, name="PylearnCBT"),
    path('dashboard', views.dashboard, name='dashboard'),
    path('email_verification', views.verification_success, name='verification_success'),
    path('verification/<uidb64>/<token>', views.activate_user, name='verification'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('save_exam', views.save_exam, name='save_exam'),
    path('verify_login', views.verify_exam_login, name='verify_login'),
    path('export-to-excel/<uuid:exam_id>', views.export_to_excel, name='export_to_excel'),
    path('delete_exam/<uuid:exam_id>', views.delete_exam, name='delete_exam'),
    path('logout', views.logout, name='logout'),
    path("my_exams/", views.my_exams, name="my_exams"),  # New exam (redirects)
    path("my_exams/<uuid:uuid>", views.my_exams, name="my_exams"),
    path('my_exam_settings', views.my_exam_settings, name='my_exam_settings'),
    path("publish_exam", views.publish_exam, name="publish_exam"),
    path("end_exam", views.end_exam, name="end_exam"),
    path('resend-verification', views.resend_verification_link, name='resend-verification'),
    path("delete_response/<uuid:exam_id>/<str:candidate_id>", views.delete_response, name='delete_response'),
    path('feedback', views.Feedback, name='feedback'),
    path('upload_questions', views.Upload_Question, name='upload_questions'),
    path('feedback_response', views.submit_feedback, name='feedback_response'),
    path('exam-id=<uuid:uuid>/take/<str:published_hash>', views.view_exam, name='view_exam'),
    path('save_exam_answer', views.save_exam_answer, name='save_exam_answer'),
  
]





