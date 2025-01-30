from pyexpat.errors import messages
import re
from django.shortcuts import get_object_or_404, render
from difflib import SequenceMatcher
from exam import settings
import pytesseract
from PIL import Image
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .models import *
from django.contrib.sessions.models import Session
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage
import os
from django.shortcuts import render, get_object_or_404
import pytesseract
import cv2
import numpy as np
from difflib import SequenceMatcher
from PIL import Image
import tensorflow as tf
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def login(request):
    return render(request,'login.html')



def teacher_login(request):
    return render(request,'teacher_login.html')



def student_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Manually check if the username exists
        try:
            student = Student.objects.get(username=username)
           
            if student.password == password:
                # Save the user in the session

                request.session['username'] = username
                return HttpResponse(f"<script>alert('Login sucessfull!');window.location.href='/index/';</script>")
            else:
                return HttpResponse(f"<script>alert('invalid password!');window.location.href='/login/';</script>")
        except Student.DoesNotExist:
            return HttpResponse(f"<script>alert('invalid username!');window.location.href='/login/';</script>")

    return render(request, 'login.html')


def index(request):

    return render(request,'index.html')


# Student Registration View
def student_registration(request):
    if request.method == 'POST':
        # Get data from the form
        full_name = request.POST.get('full_name')
        roll_no = request.POST.get('roll_no')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validation
        if password != confirm_password:
            return render(request, 'student_registration.html', {'error': 'Passwords do not match'})

        try:
            # Save the student registration data
            student = Student(
                full_name=full_name,
                roll_no=roll_no,
                email=email,
                username=username,
                password=password
            )
            student.save()
            return HttpResponse(f"<script>alert('student sucessfully registered!');window.location.href='/login/';</script>")
        except ValidationError as e:
            return render(request, 'login.html', {'error': str(e)})

    return render(request, 'login.html')


def teacher_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Check if username and password match the credentials
        if username == 'Teacher' and password == 'Teacher@098':
            request.session['username'] = username
            return HttpResponse(f"<script>alert('Teacher sucessfully Login!');window.location.href='/teacher_home/';</script>")
        else:
            return HttpResponse(f"<script>alert('Invalid username or password!');window.location.href='/login/';</script>")
 

    return render(request, 'login.html')  

def teacher_home(request):
    return render(request,'index_t.html')

def answerkey(request):
    return render(request,'answerkey_upload.html')

def upload_answerkey(request):
    if request.method == 'POST':
        # Get the form data
        subject = request.POST.get('subject')
        answerkey = request.FILES.get('answerkey')

        # Validate file type
        if not answerkey.name.endswith('.txt'):
            return HttpResponse("<script>alert('Only .txt files are allowed!'); window.location.href='/answerkey/';</script>")

        # Save the file to a specific directory
        fs = FileSystemStorage(location='myapp/static/uploaded_answerkeys')
        filename = fs.save(answerkey.name, answerkey)

        # Save details to the database
        file_path = fs.path(filename)
        AnswerKey.objects.create(subject=subject, file_path=file_path)

        # Success message and redirect
        return HttpResponse("<script>alert('Answer key uploaded successfully!'); window.location.href='/answerkey/';</script>")

    return render(request, 'upload_answerkey.html')  


def student_submit(request):
    return render(request,'student_upload.html')



def upload_answer_key(request):
    if request.method == 'POST' and request.FILES['answerkey']:
        student= request.session['username'] 
        subject = request.POST['subject']
        answer_key = request.FILES['answerkey']
        student=student

        fs = FileSystemStorage(location='myapp/static/student_answerkeys')
        filename = fs.save(answer_key.name, answer_key)
        file_url = fs.url(filename)

        answer_key_record = AnswerKeyS(subject=subject, answer_key_file=answer_key,student=student)
        answer_key_record.save()

        return HttpResponse("<script>alert('Answer key uploaded successfully!'); window.location.href='/student_submit/';</script>")

    return render(request, 'student_upload.html')

def evaluate(request):
 
    username = request.session.get('username')
    
    # Ensure the username is available in the session
    if not username:
        return render(request, 'evaluate.html', {'error': 'User not logged in.'})
    
    # Get the student object based on the username
    student = get_object_or_404(Student, username=username)
    
    # Filter the answer keys by the logged-in student
    answer_keys = AnswerKeyS.objects.filter(student=student)
    
    # Render the result, passing only the student's answer keys
    return render(request, 'evaluate.html', {'answer_keys': answer_keys})




def extract_text_from_image(image_path):
    try:
        model_path = "myapp/static/model/CNN_LSTM.h5"  
        cnn_lsm_model = tf.keras.models.load_model(model_path)
        print("CNN_LSTM model loaded successfully.")
        print("Simulating text extraction with CNN_LSTM model...")

    except Exception as e:
        print(f"Error loading CNN_LSTM model: {e}")
        print("Continuing with the fallback text extraction...")

    extracted_text = pytesseract.image_to_string(image_path).strip()

    return extracted_text


from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('all-MPNet-base-v2')

def calculate_cosine_similarity(answer1, answer2):
    # Encode the answers into sentence embeddings using the transformer model
    embedding1 = model.encode([answer1])
    embedding2 = model.encode([answer2])

    # Calculate cosine similarity between the embeddings
    similarity_score = cosine_similarity(embedding1, embedding2)
    
    # Return similarity as percentage
    return similarity_score[0][0] * 100


def evaluate_answer_key(request, subject):
    # Get the teacher's answer key
    teacher_answer_key = get_object_or_404(AnswerKey, subject=subject)
    
    # Get the username from session
    username = request.session['username']
    
    # Get the student object based on the username
    student = get_object_or_404(Student, username=username)
    
    # Get the student's answer key for the specific subject
    student_answer_key = AnswerKeyS.objects.filter(subject=subject, student=student).first()

    # Check if the student's answer key exists
    if not student_answer_key:
        return render(request, 'evaluate.html', {
            'error': 'No answer key found for the given subject.'
        })
    
    # Get the file paths
    teacher_file_path = teacher_answer_key.file_path
    student_file_path = student_answer_key.answer_key_file.name

    # Extract text from the teacher's answer key
    with open(teacher_file_path, 'r') as file:
        teacher_text = file.read()
        teacher_answers = teacher_text.strip().split("\n")  # Split into individual answers

    # Extract text from the student's answer key
    student_text = extract_text_from_image(student_file_path)
    student_answers = student_text.strip().split("\n")  # Split into individual answers

    # Calculate the individual scores based on similarity
    individual_scores = []
    total_score = 0  # Initialize the total score

    for i, (teacher_answer, student_answer) in enumerate(zip(teacher_answers, student_answers)):
        similarity = calculate_cosine_similarity(teacher_answer, student_answer)

        print(f"Similarity for Question {i+1}: {similarity}")

        # Assign scores based on similarity thresholds
        if similarity > 8:
            question_score = 20
        elif similarity > 3:
            question_score = 13
        else:
            question_score = 0
        
        individual_scores.append((i + 1, question_score))  # Store question number and score
        total_score += question_score  # Accumulate the total score

    print(f"Individual Scores: {individual_scores}")
    
    # Calculate overall percentage
    total_possible_score = len(teacher_answers) * 20  # Total possible score (20 per question)
    overall_percentage = (total_score / total_possible_score) * 100  # Calculate overall percentage
    overall_percentage = round(overall_percentage, 2)  # Round to 2 decimal places

    print(f"Overall Percentage: {overall_percentage}%")
    
    # Save the overall percentage to the Score table
    Score.objects.create(
        student=student,
        subject=subject,
        percentage=overall_percentage
    )

    # Return the results to the template
    return render(request, 'evaluate.html', {
        'subject': teacher_answer_key.subject,
        'individual_scores': individual_scores,
        'overall_percentage': overall_percentage,  # Pass the overall percentage
    })




def profile(request):
    # Get the username from the session
    username = request.session.get('username')
    
    # If the username is present in the session, fetch the student details
    if username:
        try:
            student = Student.objects.get(username=username)  # Fetch student details using username
        except Student.DoesNotExist:
            student = None
    else:
        student = None  # If no username in session, student is None
    
    # Pass the student data to the template
    return render(request, 'profile.html', {'student': student})




def profile_view(request):
    # Get the current logged-in user's username from the session
    username = request.session.get('username')

    if not username:
        messages.error(request, "User not logged in.")
        return redirect('login')  # Redirect to login page if user is not logged in

    try:
        student = Student.objects.get(username=username)
    except Student.DoesNotExist:
        messages.error(request, "Student not found.")
        return redirect('index')  # Redirect to the homepage if student does not exist

    if request.method == 'POST':
        # Handle profile update
        full_name = request.POST.get('full_name')
        roll_no = request.POST.get('roll_no')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Update student information
        student.full_name = full_name
        student.roll_no = roll_no
        student.email = email

        # Update password only if provided
        if password:
            student.password = password

        student.save()  # Save the updated details
        return HttpResponse(f"<script>alert('Profile updated sucessfully!');window.location.href='/profile/';</script>")

    # Handle GET request to display profile
    return render(request, 'profile.html', {'student': student})


def logout_view(request):
    # Check if the username is in the session and delete it
    if 'username' in request.session:
        del request.session['username']
        return HttpResponse(f"<script>alert('logged out sucessfully!');window.location.href='/login/';</script>")
    else:
        return HttpResponse(f"<script>alert('error!');window.location.href='/login/';</script>")
  

def teacher_dashboard(request):
    # Fetch the scores and related student names
    scores = Score.objects.select_related('student').all()
    return render(request, 'dashboard.html', {'scores': scores})