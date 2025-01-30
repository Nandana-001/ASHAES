from django.db import models

class Student(models.Model):
    full_name = models.CharField(max_length=255)
    roll_no = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)
    

    def __str__(self):
        return self.username


class AnswerKey(models.Model):
    subject = models.CharField(max_length=100)
    file_path = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject
    
class AnswerKeyS(models.Model):
    subject = models.CharField(max_length=255)
    student = models.CharField(max_length=255)
    answer_key_file = models.FileField(upload_to='answer_keys/')  

    def __str__(self):
        return self.subject


class Score(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='scores')
    subject = models.CharField(max_length=255)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.student.username} - {self.subject} - {self.percentage}%"
