import hashlib
import os
from django.contrib import messages
import re
from datetime import timezone, timedelta
from io import TextIOWrapper
from django.conf import settings
import requests
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib.auth.models import User
from django.contrib import auth
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from concurrent.futures import ThreadPoolExecutor
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseRedirect
import json
import threading
from concurrent.futures import ThreadPoolExecutor
import random
import datetime
import openpyxl
from django.http import HttpResponse
from openpyxl.styles import Alignment
from .models import Exam, Question, MultipleChoiceOption, ExamSetting, ExamAnswer, Email_Verification, UserProfile
from django.middleware.csrf  import get_token

from .models import Email_Verification, UserProfile
from django.shortcuts import render, redirect
from .utils import generate_token, resend_verfication
from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone
from django.urls import reverse
import uuid
from django.views.decorators.cache import never_cache

def Send_Email_Verification_msg(request, user):
   try:
    current_site  = get_current_site(request)
    email_subject = 'Verify your email'
    token=generate_token.make_token(user)
    make_token_user = Email_Verification.objects.get(user=user)
    make_token_user.make_token = token
    make_token_user.save()
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

    email_body = render_to_string('verification_center.html',{'user':user, 'domain': current_site,
                                                              'uidb64':uidb64, 'token':token, 'year':2024})
    plain_text=strip_tags(email_body)
    send_mails= EmailMultiAlternatives(subject=email_subject, body=plain_text, from_email='Nexapy CBT <no-reply@nexapytechnologies.com>', to=[user.email])
    send_mails.attach_alternative(email_body,'text/html')
    send_mails.send(fail_silently=False)
   except Exception as e:
       print(f'email verification not sent for {user.username} error code{e}')



def normalize_answer(answer):
    # Normalize by removing extra spaces and converting to lowercase
    return re.sub(r'\s+', ' ', answer.strip()).lower()
import spacy

# Load the spaCy model
# Load the spaCy model
nlp = spacy.load("en_core_web_md")

# Helper function to normalize answers
def normalize_answer(answer):
    # Standardize the answer (trim and lowercase)
    return answer.strip().lower()
def mark_theory_answer(candidate_answer, correct_answer, threshold=0.7, key_point_weight=0.4, semantic_weight=0.5, relevance_weight=0.1):
    """
    Marks a theoretical answer based on semantic similarity, completeness, and relevance.

    Args:
        candidate_answer (str): The candidate's answer.
        correct_answer (str): The reference or correct answer.
        threshold (float): The similarity threshold for semantic matching.
        key_point_weight (float): Weight for the completeness score.
        semantic_weight (float): Weight for the semantic similarity score.
        relevance_weight (float): Weight for deducting irrelevant content.

    Returns:
        dict: A detailed breakdown of scores and feedback.
    """
    if not candidate_answer or not correct_answer:
        return {
            "error": "Either the candidate's answer or the correct answer is missing."
        }

    # Process and calculate similarity
    candidate_doc = nlp(candidate_answer.strip().lower())
    correct_doc = nlp(correct_answer.strip().lower())

    try:
        semantic_similarity = candidate_doc.similarity(correct_doc)
    except ValueError:
        semantic_similarity = 0  # Fallback for missing vectors

    # Assess completeness
    correct_key_points = [token.text.lower() for token in correct_doc if not token.is_stop and not token.is_punct]
    candidate_key_points = [token.text.lower() for token in candidate_doc if not token.is_stop and not token.is_punct]

    matched_points = len(set(candidate_key_points).intersection(set(correct_key_points)))
    completeness_score = matched_points / len(correct_key_points) if correct_key_points else 0

    # Assess relevance
    irrelevant_points = len(set(candidate_key_points) - set(correct_key_points))
    relevance_penalty = irrelevant_points / len(candidate_key_points) if candidate_key_points else 0

    # Weighted total score
    total_score = (
        (semantic_weight * semantic_similarity) +
        (key_point_weight * completeness_score) -
        (relevance_weight * relevance_penalty)
    )

    return {
        "semantic_similarity": semantic_similarity,
        "completeness_score": completeness_score,
        "relevance_penalty": relevance_penalty,
        "total_score": total_score
    }
def mark_exam(candidate_id, exam_id):
    # Fetch the exam and candidate answers using provided IDs
    exam = get_object_or_404(Exam, uuid=exam_id)
    candidate_answer_record = get_object_or_404(ExamAnswer, candidate_id=candidate_id, exam=exam)

    # Extract the exam questions and candidate answers
    exam_questions = exam.questions_data
    candidate_answers = candidate_answer_record.answers_data

    # Convert candidate answers to a dictionary for quick lookup by question id
    candidate_answers_dict = {str(answer["id"]): answer for answer in candidate_answers}

    # Initialize score and feedback
    score = 0
    total_questions = len(exam_questions)
    feedback = []

    # Iterate over exam questions and evaluate answers
    for question in exam_questions:
        question_id = str(question.get("id"))
        question_type = question.get("type")
        correct_answer = question.get("answers")
        question_title = question.get("title")

        # Default candidate response to empty if not answered
        candidate_response = candidate_answers_dict.get(question_id, {}).get("answers", "")
        candidate_response = candidate_response.strip() if candidate_response else ""

        # Build feedback object
        question_feedback = {
            "question_id": question_id,
            "type": question_type,
            "question_title": question_title,
            "candidate_answer": candidate_response,
            "correct_answer": correct_answer,
            "status": "",
            "details": ""
        }

        # If answer is missing
        if not candidate_response:
            question_feedback["status"] = "Unattempted"
            feedback.append(question_feedback)
            continue

        # Marking logic
        if question_type == "multiple-choice":
            if normalize_answer(candidate_response) == normalize_answer(correct_answer):
                score += 1
                question_feedback["status"] = "Correct"
            else:
                question_feedback["status"] = "Incorrect"

        elif question_type in ["short-answer", "paragraph"]:
            result = mark_theory_answer(candidate_response, correct_answer)
            total_score = float(result.get("total_score", 0))
            if total_score >= 0.5:
                score += 1
                question_feedback["status"] = "Correct"
            else:
                question_feedback["status"] = "Incorrect"
            question_feedback["details"] = result

        else:
            question_feedback["status"] = "Unsupported question type"

        feedback.append(question_feedback)

    # Calculate overall percentage
    percentage = round((score / total_questions) * 100, 2) if total_questions else 0

    # Update candidate's exam record
    candidate_answer_record.status = percentage >= 50
    candidate_answer_record.score = score
    candidate_answer_record.percentage = percentage
    candidate_answer_record.save()

    return JsonResponse({
        "success": True,
        "message": "Exam marked successfully.",
        "score": score,
        "percentage": percentage,
        "total_questions": total_questions,
        "feedback": feedback,
    })


'''def mark_exam(candidate_id, exam_id):
    # Fetch the exam and candidate answers using provided IDs
    exam = get_object_or_404(Exam, uuid=exam_id)
    candidate_answer_record = get_object_or_404(ExamAnswer, candidate_id=candidate_id, exam=exam)

    # Extract the exam questions and candidate answers
    exam_questions = exam.questions_data
    candidate_answers = candidate_answer_record.answers_data

    # Convert candidate answers to a dictionary for quick lookup by question id
    candidate_answers_dict = {str(answer["id"]): answer for answer in candidate_answers}

    # Initialize score and feedback
    score = 0
    total_questions = len(exam_questions)
    feedback = []

    # Iterate over exam questions and evaluate answers
    for question in exam_questions:
        question_id = str(question.get("id"))
        candidate_answer = candidate_answers_dict.get(question_id, {})  # Find matching candidate answer by ID

        correct_answer = question.get("answers")  # Correct answer for the question
        candidate_response = candidate_answer.get("answers", "").strip()  # Candidate's response

        question_type = question.get("type")  # Question type
        question_feedback = {
            "question_id": question_id,
            "type": question_type,
            "question_title": question.get("title"),
            "candidate_answer": candidate_response,
            "correct_answer": correct_answer,
            "status": "",  # Status of the answer (Correct, Incorrect, Unattempted)
            "details": ""  # Additional feedback details
        }

        # If no answer is provided
        if not candidate_response:
            question_feedback["status"] = "Unattempted"
            feedback.append(question_feedback)
            continue

        # Marking based on question type
        if candidate_response and question_type == "multiple-choice":
            # For multiple-choice questions, check if the candidate's answer matches the correct answer
            if normalize_answer(candidate_response) == normalize_answer(correct_answer):
                score += 1
                question_feedback["status"] = "Correct"
            else:
                question_feedback["status"] = "Incorrect"
        elif candidate_response and question_type in ["short-answer", "paragraph"]:
            # Use mark_theory_answer() for short-answer and paragraph questions
            result = mark_theory_answer(candidate_response, correct_answer)

            # Update the score based on the result
            total_score = result.get("total_score", 0)
            #print(total_score)
            if float(total_score) >= 0.5:
                score += 1
                question_feedback["status"] = "Correct"
            else:
                question_feedback["status"] = "Incorrect"

            # Include detailed feedback for the question
            question_feedback["details"] = result
        else:
            question_feedback["status"] = "Unsupported question type"

        feedback.append(question_feedback)

    # Calculate overall percentage
    percentage = round((score / total_questions) * 100, 2) if total_questions else 0

    # Update candidate's exam record with the score, percentage, and status
    candidate_answer_record.status = percentage >= 50  # Pass if percentage is 50 or above
    candidate_answer_record.score = score
    candidate_answer_record.percentage = percentage

    # Save the updated candidate answer record
    candidate_answer_record.save()

    # Return the response with marking results
    return JsonResponse({
        "success": True,
        "message": "Exam marked successfully.",
        "score": score,
        "percentage": percentage,
        "total_questions": total_questions,
        "feedback": feedback,
    })

'''
# Create your views here.
#----------------------------user signup route--------------------------
def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request,  'index.html')
def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm-password']
        if password == confirm_password:
            if len(password) < 8:
                return JsonResponse({'error': 'password should be in 8 characters'})
            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': f'{email} already exists'})
            elif User.objects.filter(username=username).exists():
                return JsonResponse({'error': f'{username} already taken'})
            else:
                user = User.objects.create_user(username=username, email=email, password=confirm_password)
                user_model = User.objects.get(username=username)
                UserProfile.objects.create(user=user_model)

                try:
                    # Submit the email sending task to a thread pool.
                    executor = ThreadPoolExecutor(
                        max_workers=1)  # Optionally, set the max_workers to 1 since it's just one task.
                    executor.submit(Send_Email_Verification_msg, request, user)
                      # Do not wait for the thread to finish.

                    # Return the JSON response immediately.
                    return JsonResponse({
                        'success': 'Your account has been successfully created! Please check your email to verify your account and activate it.'
                    })

                except Exception as e:
                    user.Delete()
                    UserProfile.Delete()
                     # Log the exception (use logging in production).
                    return JsonResponse({'error': 'Something went wrong'})
        else:
            return JsonResponse({'error': 'Passwords do not match'})
    else:return redirect('/')

def signin(request):
    if request.method == 'POST':
        username = request.POST['susername']
        password = request.POST['spassword']
        user = auth.authenticate(username=username, password=password)

        if user is not None :
            auth.login(request, user)
            return JsonResponse({'success':'/dashboard'})

        else:
            return JsonResponse({'error': 'Email address or password is invalid'})
    else:
        if request.user.is_authenticated:
             return redirect('/dashboard')
        else:
             return redirect('/')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')



@csrf_exempt
def activate_user(request, uidb64, token):
    try:
        # Decode the user ID from the URL
        User = get_user_model()
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        # Fetch the verification record
        verification = get_object_or_404(Email_Verification, user=user)

        # Check if the request is a GET request
        if request.method == "GET":
            current_time = timezone.now()
            expiration_time = verification.timestamp + timedelta(minutes=50)

            # Verification conditions
            if verification.make_token == token:
                if current_time > expiration_time:
                    return HttpResponse('Link expired')
                if verification.is_email_verified:
                    return HttpResponse('Email already verified, kindly login')

                else:# Mark as verified and update token
                    verification.is_email_verified = True
                    verification.full_token = f'{verification.token}{verification.timestamp}{verification.is_email_verified}'
                    verification.save()
                    response = redirect('verification_success')
                    response.set_signed_cookie('verification_success', 'true', salt='email', max_age=400)
                    return response
            else:
                return HttpResponse('Invalid token')
        else:
            return HttpResponse('Invalid request method')
    except Exception as e:
        # Log the exception (for debugging)
        print(f"Error during user activation: {e}")
        return HttpResponse('Invalid link or an error occurred')


def verification_success(request):
    try:
        if request.get_signed_cookie('verification_success', salt='email'):
            return render(request, 'activate_email.html', {'message': 'Email successfully verified!'})
    except KeyError:
        pass  # Cookie doesn't exist or is invalid

    return render(request, 'activate_email.html', {'message': 'Invalid or expired verification.'})

@login_required(login_url='signin')
def dashboard(request):

    now = timezone.now()
    profile = get_object_or_404(UserProfile , user = request.user)
 
   

    base_url = f"{request.scheme}://{request.get_host()}"
    user=request.user

    exams = Exam.objects.filter(user=user).order_by('-updated_at')
    is_published= [exam.is_published for exam in exams]




    exam_response = ExamAnswer.objects.filter(user=user)
    try:
        # Attempt to fetch the Email_Verification object
        email_verify = get_object_or_404(Email_Verification, user=user)

    except Exception as e:
        # Handle the case where the object does not exist or other errors
        email_verify = None  # Ensure email_verify is defined


    # Define the context with a safe fallback for email_verified
    context = {
        'exams': exams,
        'total_exam': exams.count(),
        'edit_exam': f'{base_url}/my_exams',
        'exam_response': exam_response.count(),
        'is_published': is_published.count(True),
        'email_verified': email_verify.is_email_verified if email_verify else False,  # Use a fallback if email_verify is None
        'profile': profile
    }
    return render(request, 'dashboard.html', context)

@login_required(login_url='signin')
def export_to_excel(request, exam_id):
    try:
        # Fetch the exam and settings
        exam = get_object_or_404(Exam, uuid=exam_id)
        exam_settings = get_object_or_404(ExamSetting, exam=exam)

        # Fetch results for the specific exam
        results = ExamAnswer.objects.filter(exam=exam)

        # Create an Excel workbook and worksheet
        wb = openpyxl.Workbook()
        ws = wb.active
        headers = [
            "Candidate ID",
            f"Score / {len(exam.questions_data)}",
            "Percentage (100%)",
            "Time Taken",
            "Status",
            "Submitted At",
        ]
        ws.append(headers)

        # Set alignment for the headers
        for col in ws.iter_cols(min_row=1, max_row=1, min_col=1, max_col=len(headers)):
            for cell in col:
                cell.alignment = Alignment(horizontal="center", vertical="center")

        # Add data rows
        for result in results:
            score = int(result.score)
            total_questions = len(exam.questions_data)
            percentage = round((score / total_questions) * 100, 2)

            row = [
                result.candidate_id,
                score,
                percentage,
                f"{exam_settings.countdown_time} secs.",
                "Pass" if result.status else "Fail",
                f'{result.submitted_at} UTC+1',
            ]
            ws.append(row)

        # Prepare the response for the Excel file
        filename = f"Exam_Results_{exam.title}_{datetime.date.today()}.xlsx"
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        # Save the workbook to the response
        wb.save(response)

        # Return the Excel file as the response
        return response

    except Exception as e:
        # Handle errors gracefully and provide meaningful feedback
        return JsonResponse({'error': str(e)})

@login_required(login_url='signin')
def my_exams(request, uuid=None):
    now = timezone.now()
    profile = get_object_or_404(UserProfile , user = request.user)

    if uuid is None:
        if not profile.subscription_active:
            exam = Exam.objects.filter(user=request.user)
            if exam.exists():
               return redirect('subscription')  # Redirect to subscription page
            else:
                new_exam = Exam.objects.create(user=request.user)
                ExamSetting.objects.create(exam=new_exam)
        else:
           new_exam = Exam.objects.create(user=request.user)
           ExamSetting.objects.create(exam=new_exam)

        return redirect("my_exams", uuid=new_exam.uuid)
    exam = get_object_or_404(Exam, uuid=uuid)
    exam_setings = get_object_or_404(ExamSetting, exam=exam)
    exam_response = ExamAnswer.objects.filter(exam=exam).order_by('-submitted_at')
    json_question = exam.questions_data
    total_exam = len(json_question)





    context={
        'exam':exam,
        'json_question':json_question,
        'exam_settings':exam_setings,
        'exam_response': exam_response,
        'total_exam': total_exam,
        'profile': profile

    }

    return render(request, 'my_exams.html', context )



from django.core.files.storage import FileSystemStorage
import pandas as pd
def Upload_Question(request):
  try:
    profile = get_object_or_404(UserProfile , user = request.user)

    if request.method == 'POST' and request.FILES['questions_excel_file'] :
            exam_id = request.POST.get('exam-id')
            excel_file = request.FILES['questions_excel_file']
            # Save the file temporarily
            fs = FileSystemStorage()
            file_path = fs.save(excel_file.name, excel_file)
            file_path = fs.path(file_path)

            # Load the file with pandas
            try:
                df = pd.read_excel(file_path)

                # Validate required columns
                required_columns = ['Type', 'Title', 'Answers', 'Options']
                if not all(col in df.columns for col in required_columns):
                    return JsonResponse({'error': "The Excel file does not contain the required columns."})

                # Convert DataFrame to JSON format
                questions = []
                for  index, row in df.iterrows():
                    question = {
                        'id': index + 1,
                        'type': row['Type'],
                        'title': row['Title'],
                        'answers': row['Answers'] if not pd.isna(row['Answers']) else "",
                        'options': [opt.strip() for opt in str(row['Options']).split(',')] if not pd.isna(row['Options']) else []
                    }
                    questions.append(question)

                # Save to the Exam model
                exam = Exam.objects.get(uuid=exam_id)
                exam.questions_data = questions
                exam.save()

                return JsonResponse({'success': "Questions uploaded successfully!"})


            except Exception as e:
                return  JsonResponse({'error':f"Error processing the file"})
  except Exception as e:
        return redirect('dashboard')


@csrf_exempt
def delete_exam(request, exam_id):
    try:
        profile = get_object_or_404(UserProfile , user = request.user)
    
        if request.method=='POST':
            if exam_id:
                #exam_id = request.POST.get('exam-id')
                exam = get_object_or_404(Exam, uuid=exam_id)

                exam.delete()
                return JsonResponse({'message': 'Exam deleted successfully'}, status=200)
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    except Exception as e:
        return redirect('/')
@csrf_exempt
def delete_response(request, exam_id,  candidate_id):
    if request.method=='POST':
        if candidate_id:
            exam = get_object_or_404(Exam, uuid=exam_id)
            candidate_response = get_object_or_404(ExamAnswer, exam=exam , candidate_id=candidate_id)
            candidate_response.delete()
            return JsonResponse({'message': 'response  deleted successfully'})
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def publish_exam(request):
    if request.method=='POST':
        uuid = request.POST.get('uuid')
        # Get the exam by UUID

    exam = get_object_or_404(Exam, uuid=uuid, user=request.user)
    verify_email = get_object_or_404(Email_Verification, user=request.user)
    print(verify_email.is_email_verified)
    print(request.user.username)

    # If the exam is not already published, publish it
    if verify_email.is_email_verified:
        if not exam.is_published:
            exam.is_published = True
            exam.save()  # Save the exam to trigger the `published_hash` generation
            base_url = f"{request.scheme}://{request.get_host()}"
            publish_url=  f"{base_url}/exam-id={uuid}/take/{exam.published_hash}"
            exam.published_url = publish_url
            exam.save()
            # Generate the publish URL for the exam
            publish_url = exam.published_url # This uses the `get_publish_url` method

            # Return a success response with the published URL
            return JsonResponse({ 'success':  publish_url})
        else:
            return JsonResponse({'error': 'exam already published\nkindly check your dashboard'})
    else:
        return JsonResponse({'error': 'email address not verified\nkindly verify your email'})
def candidate_list(file, exam):
    candidate_id_file = file
    if candidate_id_file.name.endswith('.csv'):
        candidates = parse_csv(candidate_id_file)
        return candidates
    elif candidate_id_file.name.endswith('.txt'):
        candidates = parse_txt(candidate_id_file)
        return candidates
    elif candidate_id_file.name.endswith('.xlsx'):
        candidates = parse_excel(candidate_id_file)
        return candidates
    else:
        return JsonResponse({"success": False, "error": "Unsupported file format."})

def parse_csv(file):
    # Open the file from the uploaded file object stored in the database
    with file.open('r') as f:
        import csv
        reader = csv.reader(f)
        candidates = [row[0].strip() for row in reader if row]  # Extract names or values from the CSV
    return candidates

def parse_txt(file):
    with file.open('r') as f:
        lines = f.readlines()  # Read lines
        candidates = [line.strip() for line in lines if line]
    return candidates

def parse_excel(file):
    import pandas as pd
    # Use pandas to read the Excel file
    df = pd.read_excel(file)
    candidates = df.iloc[:, 0].dropna().astype(str).tolist()  # Assuming names are in the first column
    return candidates


def verify_exam_login(request):
        if request.method == 'POST':
            if request.session.get("is_logging_in"):
                return JsonResponse({"backend": "Login already in progress. Please wait."}, status=429)

            request.session["is_logging_in"] = True  # Set lock
            try:
                # Parse the JSON body
                data = json.loads(request.body)

                candidate_id = data.get('candidate_id').lower()
                published_id = data.get('publish_id')
                uuid = data.get('uuid')


                # Fetch the exam and its settings
                exam = get_object_or_404(Exam, published_hash=published_id, uuid=uuid)
                exam_settings = get_object_or_404(ExamSetting, exam=exam)

                # Extract candidate list from the uploaded file
                candidates = [candidate.lower() for candidate in candidate_list(file=exam_settings.uploaded_file, exam=exam)]


                # Check if candidate_id is in the candidate list
                if candidate_id in candidates:

                    # Check if the candidate has already participated in the exam
                    if ExamAnswer.objects.filter(candidate_id=candidate_id, exam=exam).exists():
                        request.session.pop('candidate_id', None)


                        return JsonResponse({'candidate_exists': 'You have already participated in the exam'})

                    else:
                           # Save candidate_id in the session and set session expiry
                        request.session.flush()
                        request.session['candidate_id'] = candidate_id


                        user = exam.user
                        ExamAnswer.objects.create(
                            user=user,
                            candidate_id=candidate_id,
                            exam=exam,
                            is_candidate_logined=True
                        )



                        return JsonResponse({'success': 'Exam_ logined'})
                else:
                         return JsonResponse({'invalid': 'Invalid Candidate ID'})
            except Exception as e:
                 # Catch and log the error for debugging
                 return JsonResponse({'error': f'An error occurred: {str(e)}'})
            finally:
                # Always release the lock, even if error occurs
                request.session["is_logging_in"] = False

def view_exam(request, uuid, published_hash):

    reload_count = 0
    # Get the exam based on UUID and hash
    exam = get_object_or_404(Exam, uuid=uuid, published_hash=published_hash)
    candidate_id = request.session.get('candidate_id')

    exam_settings = get_object_or_404(ExamSetting, exam=exam)

    # Prepare the exam method context
    exam_method_context = {
        'id': exam_settings,
        'exam': exam
    }

    try:

        # Get the exam based on UUID and hash

        exam = get_object_or_404(Exam, uuid=uuid, published_hash=published_hash)
        candidate_id = request.session.get('candidate_id')

        # If candidate ID is not set in session, redirect to candidates page
        if not candidate_id:
            return render(request, 'candidates.html', exam_method_context)

        # Check if the candidate has already attempted the exam
        try:
            is_candidate_login = get_object_or_404(ExamAnswer, exam=exam, candidate_id=candidate_id)

            if is_candidate_login.is_candidate_logined and not is_candidate_login.end_exam:
                # Increment reload count for GET requests

                if  is_candidate_login.is_candidate_logined  and not is_candidate_login.end_exam and request.method == 'GET':

                    old_session = int(request.session.get('reload_count', 0))  # Default to 0 if not set
                    new_session = old_session + 1  # Increment the old session count
                    request.session['reload_count'] = new_session  # Update the session with the new count
                    # Debug print to check values
                    print(f'This is old session: {old_session}, new session: {new_session}')

                    if new_session > 1:
                        # Clear candidate session data
                        request.session.pop('candidate_id', None)
                        # Optionally, clear the reload count as well
                        request.session.pop('reload_count', 0)
                        # Redirect or render a template to handle unauthorized access

                        return render(request, 'candidates.html', exam_method_context)


                questions_data = exam.questions_data

                # Shuffle questions if shuffle setting is enabled
                if exam_settings.shuffle_questions:
                    random.shuffle(questions_data)



                # Render the exam-taking page
                context = {
                    'exam': exam,
                    'questions_data': questions_data,
                    'settings': exam_settings,
                    'candidate_id': candidate_id,


                }



                return render(request, 'take_exam.html', context)

            else:
                return render(request, 'candidates.html', exam_method_context)

        except Exception as e:
            is_candidate_login = None
            return render(request, 'candidates.html', exam_method_context)
    except Exception as e:
        return  render(request, 'candidates.html', exam_method_context)
@login_required(login_url='signin')
def my_exam_settings(request):
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method=='POST':
        uuid = request.POST.get('uuid')
        time_limit = request.POST.get('time-limit')
        candidate_method = request.POST.get('candidate-method')  # Default to empty string if not provided
        candidate_file = request.FILES.get('candidate-file')  # Default to empty string if not provided

        shuffle_questions = request.POST.get('shuffle-questions') == 'on'
        enable_feedback = request.POST.get('enable-feedback') == 'on'
        enable_browser_lock = request.POST.get('enable-browser-lock') == 'on'
        exam = get_object_or_404(Exam, uuid=uuid)
        exam_settings = get_object_or_404(ExamSetting, exam=exam)
        exam_settings.countdown_time = time_limit
        exam_settings.shuffle_questions = shuffle_questions
        
        exam_settings.enable_feedback = enable_feedback
        exam_settings.enable_browser_lock = enable_browser_lock
        exam_settings.select_method = candidate_method
        if candidate_file is not None:
            exam_settings.uploaded_file = candidate_file
        exam_settings.save()
        return JsonResponse({'success': 'settings saved succesfully'})


@csrf_exempt
def save_exam_answer(request):
    if request.method == 'POST':
        try:
            # Parse the JSON body
            candidate_id = request.session.get('candidate_id')
            data = json.loads(request.body)
           
            # Extract required fields
            exam_uuid = data.get('uuid', '').strip()
            publish_hash =  data.get('publish_hash', '').strip()
            questions_answer = data.get('questions', [])
            exam = get_object_or_404(Exam, uuid=exam_uuid, published_hash=publish_hash)


            examAnswer = get_object_or_404(ExamAnswer,  exam=exam, candidate_id=candidate_id)
            if exam_uuid == str(exam.uuid) and publish_hash == exam.published_hash and candidate_id:
                examAnswer.answers_data = questions_answer
                examAnswer.save()
          
            return JsonResponse({'message': 'Answers saved successfully.'})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format.'}, status=400)
        except Exception as e:
            print(e)
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)
@csrf_exempt
def save_exam(request):
    if request.method == 'POST':
        try:
            profile = get_object_or_404(UserProfile, user=request.user)
            data = json.loads(request.body)

            uuid = data.get('uuid', '').strip()  # Check if a UUID is passed
            #print(data)
            exam_title = data.get('exam_title', '').strip()
            exam_description = data.get('exam_description', '').strip()
            questions_data = data.get('questions', [])  # Retrieve questions as JSON
            exam_number = len(questions_data)
            if uuid:
               
                # Update existing exam
                exam = get_object_or_404(Exam, uuid=uuid)
                exam.title = exam_title
                exam.description = exam_description
                exam.questions_data= questions_data
                exam.save()
                return JsonResponse({"message":  "saving..."})


        except Exception as e:
            return JsonResponse({'error': 'something went wrong'})

    return JsonResponse({'error':'Invalid request method'})

def candidate_login(request):
    return render(request, 'candidates.html')

def end_exam(request):
    if request.method != 'POST':
        if request.session.get("is_end_exam"):
                return JsonResponse({"backend": "exam ended clicked. Please wait."}, status=429)

        request.session["is_end_exam"]=True

    try:
        exam_id = request.POST.get('exam-uuid')
        publish_id = request.POST.get('publish-id')
        candidate_id = request.session.get('candidate_id')

        if not candidate_id:
            return JsonResponse({'success': False, 'message': 'Candidate not logged in.'})


        try:
          exam = get_object_or_404(Exam, uuid=exam_id, published_hash=publish_id)
          profile = get_object_or_404(UserProfile, user=exam.user)
          exam_settings = get_object_or_404(ExamSetting, exam=exam)

          mark_exam(candidate_id=candidate_id, exam_id=exam_id)
        except Exception as e:
            print(e)
            #logger.exception("Marking exam failed")
            return JsonResponse({'success': False, 'message': 'Failed to mark exam.'})

        exam_candidate = get_object_or_404(ExamAnswer, exam=exam, candidate_id=candidate_id)

        exam_candidate.end_exam = True
        exam_candidate.save()

        if exam_settings.enable_feedback:
            print('True')
            request.session['feed_exam_id'] = exam_id
            request.session['feed_candidate_id'] = candidate_id
            request.session.set_expiry(None)
            return JsonResponse({'success': True, 'redirect': '/feedback'})

        del request.session['candidate_id']
        return JsonResponse({'success': True, 'message': 'Exam ended successfully.'})

    except Exception as e:
        print(e)
        #logger.exception("Error in end_exam view")
        return JsonResponse({'success': False, 'message': 'An error occurred: ' + str(e)})
    finally:
        # Always release the lock, even if error occurs
        request.session["is_logging_in"] = False



# Create a thread pool executor
#executor = ThreadPoolExecutor(max_workers=5)

def resent_verification_email(user, current_site, uidb64, token, email_subject):
    email_body = render_to_string('verification_center.html', {
        'user': user,
        'domain': current_site,
        'uidb64': uidb64,
        'token': token
    })
    plain_text = strip_tags(email_body)

    send_email = EmailMultiAlternatives(
        subject=email_subject,
        body=plain_text,
        from_email='Nexapy CBT <no-reply@nexapytechnologies.com>',
        to=[user.email]
    )
    send_email.attach_alternative(email_body, 'text/html')
    send_email.send()

@login_required(login_url='signin')
def resend_verification_link(request):
    try:
        user = request.user
        verify= Email_Verification.objects.filter(user=user).exists()
        if not verify:
          Email_Verification.objects.create(user=user)

        current_site = get_current_site(request)
        email_subject = 'Verify your email'
        token = resend_verfication.make_token(user)

        resend_email_user = Email_Verification.objects.get(user=user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        resend_email_user.make_token = token
        resend_email_user.save()

        # Call the email sending function directly (synchronous)
        resent_verification_email(user, current_site, uidb64, token, email_subject)

        return JsonResponse({'success': 'New email verification sent successfully. Kindly check your mails'})
    except Exception as e:
        # Log the exception for debugging
        print(f"Error: {e}")
        return JsonResponse({'error': 'Something went wrong. Unable to send verification link'})

def Feedback(request):
    exam_id = request.session.get('feed_exam_id')
    exam = get_object_or_404(Exam, uuid=exam_id)
    context= {
      'exam': exam
    }

    return render(request, 'feedback.html', context)



def submit_feedback(request):
     if request.method == 'POST':
        try:

            data = json.loads(request.body)
            feedback_text = data.get('feedback')
            # Get the exam based on UUID and hash
            exam_id = request.session.get('feed_exam_id')
            candidate_id = request.session.get('feed_candidate_id')
            exam = get_object_or_404(Exam, uuid=exam_id)
            candidate_response = get_object_or_404(ExamAnswer, exam=exam, candidate_id=candidate_id)
            candidate_response.feedback = feedback_text
            candidate_response.save()

            #request.session.flush()
            return JsonResponse({'success': 'Thank you! Your feedback has been submitted successfully'})
        except Exception as e:
            return JsonResponse({'error': 'unable to submit feedback'})
        