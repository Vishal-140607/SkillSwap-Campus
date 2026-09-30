from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )

    name = models.CharField(max_length=100)

    department = models.CharField(max_length=100)

    year = models.IntegerField()

    bio = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Skill(models.Model):

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class StudentSkill(models.Model):

    SKILL_TYPES = [
        ('teach', 'Teach'),
        ('learn', 'Learn'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE
    )

    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE
    )

    skill_type = models.CharField(
        max_length=20,
        choices=SKILL_TYPES
    )

    class Meta:
        unique_together = ('student', 'skill', 'skill_type')

    def __str__(self):
        return f"{self.student.name} - {self.skill.name} ({self.skill_type})"


class LearningRequest(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    sender = models.ForeignKey(
        Student,
        related_name='sent_requests',
        on_delete=models.CASCADE
    )

    receiver = models.ForeignKey(
        Student,
        related_name='received_requests',
        on_delete=models.CASCADE
    )

    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.sender.name} → {self.receiver.name} ({self.skill.name})"


class Review(models.Model):

    reviewer = models.ForeignKey(
        Student,
        related_name='reviews_given',
        on_delete=models.CASCADE
    )

    reviewed_student = models.ForeignKey(
        Student,
        related_name='reviews_received',
        on_delete=models.CASCADE
    )

    rating = models.IntegerField()

    comment = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.reviewer.name} → {self.reviewed_student.name}"


class Notification(models.Model):

    student = models.ForeignKey(
        Student,
        related_name='notifications',
        on_delete=models.CASCADE
    )

    message = models.CharField(
        max_length=255
    )

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.student.name} - {self.message}"