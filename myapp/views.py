from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import (
    Student,
    Skill,
    StudentSkill,
    LearningRequest,
    Review,
    Notification
)


def send_realtime_notification(student, message):

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"user_{student.user.id}",
        {
            "type": "send_notification",
            "message": message,
        }
    )


def home(request):

    student_count = Student.objects.count()

    skill_count = Skill.objects.count()

    exchange_count = LearningRequest.objects.filter(
        status='accepted'
    ).count()

    return render(request, 'home.html', {
        'student_count': student_count,
        'skill_count': skill_count,
        'exchange_count': exchange_count,
    })


@login_required
def explore(request):

    search = request.GET.get('search', '')

    current_student = request.user.student_profile

    skills = Skill.objects.all()

    if search:
        skills = skills.filter(
            name__icontains=search
        )

    pending_requests = LearningRequest.objects.filter(
        sender=current_student,
        status='pending'
    )

    pending_pairs = {
        (request.receiver_id, request.skill_id)
        for request in pending_requests
    }

    skill_data = []

    for skill in skills:

        teachers = StudentSkill.objects.filter(
            skill=skill,
            skill_type='teach'
        ).exclude(
            student=current_student
        ).select_related('student')

        for teacher in teachers:
            teacher.has_pending_request = (
                teacher.student_id,
                skill.id
            ) in pending_pairs

        skill_data.append({
            'skill': skill,
            'teachers': teachers,
        })

    return render(request, 'explore.html', {
        'skill_data': skill_data,
        'search': search,
    })


def how_it_works(request):

    return render(request, 'how_it_works.html')


def login_view(request):

    if request.method == 'POST':

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('dashboard')

        messages.error(
            request,
            'Invalid username or password.'
        )

    return render(request, 'login.html')


def register(request):

    if request.method == 'POST':

        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not email or not password or not confirm_password:

            messages.error(
                request,
                'Please fill in all required fields.'
            )

            return render(request, 'register.html')

        if len(username) < 3:

            messages.error(
                request,
                'Username must be at least 3 characters long.'
            )

            return render(request, 'register.html')

        if len(password) < 8:

            messages.error(
                request,
                'Password must be at least 8 characters long.'
            )

            return render(request, 'register.html')

        if password != confirm_password:

            messages.error(
                request,
                'Passwords do not match.'
            )

            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():

            messages.error(
                request,
                'Username already exists.'
            )

            return render(request, 'register.html')

        if User.objects.filter(email=email).exists():

            messages.error(
                request,
                'Email is already registered.'
            )

            return render(request, 'register.html')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        Student.objects.create(
            user=user,
            name=username,
            department='',
            year=1,
            bio=''
        )

        messages.success(
            request,
            'Account created successfully! You can now log in.'
        )

        return redirect('login')

    return render(request, 'register.html')


@login_required
def dashboard(request):

    student = request.user.student_profile

    student_count = Student.objects.count()

    skill_count = Skill.objects.count()

    exchange_count = LearningRequest.objects.filter(
        status='accepted'
    ).count()

    notifications = Notification.objects.filter(
        student=student,
        is_read=False
    ).order_by('-created_at')

    notification_count = notifications.count()

    return render(request, 'dashboard.html', {
        'student': student,
        'student_count': student_count,
        'skill_count': skill_count,
        'exchange_count': exchange_count,
        'notifications': notifications,
        'notification_count': notification_count,
    })


@login_required
def profile(request):

    student = request.user.student_profile

    reviews = Review.objects.filter(
        reviewed_student=student
    ).select_related(
        'reviewer'
    ).order_by('-created_at')

    return render(request, 'profile.html', {
        'student': student,
        'reviews': reviews,
    })


@login_required
def edit_profile(request):

    student = request.user.student_profile

    if request.method == 'POST':

        name = request.POST.get('name', '').strip()
        department = request.POST.get('department', '').strip()
        year = request.POST.get('year', '').strip()
        bio = request.POST.get('bio', '').strip()

        if not name:

            return render(request, 'edit_profile.html', {
                'student': student,
                'error_message': 'Name cannot be empty.'
            })

        if not department:

            return render(request, 'edit_profile.html', {
                'student': student,
                'error_message': 'Department cannot be empty.'
            })

        try:
            year = int(year)
        except (TypeError, ValueError):

            return render(request, 'edit_profile.html', {
                'student': student,
                'error_message': 'Please enter a valid year.'
            })

        if year < 1 or year > 5:

            return render(request, 'edit_profile.html', {
                'student': student,
                'error_message': 'Year must be between 1 and 5.'
            })

        student.name = name
        student.department = department
        student.year = year
        student.bio = bio

        student.save()

        messages.success(
            request,
            'Profile updated successfully!'
        )

        return redirect('profile')

    return render(request, 'edit_profile.html', {
        'student': student,
    })


@login_required
def manage_skills(request):

    student = request.user.student_profile

    skills = Skill.objects.all()

    if request.method == 'POST':

        skill_id = request.POST.get('skill')
        skill_type = request.POST.get('skill_type')

        if not skill_id or not skill_type:

            messages.error(
                request,
                'Please select a skill and skill type.'
            )

            return redirect('manage_skills')

        allowed_types = [
            choice[0]
            for choice in StudentSkill.SKILL_TYPES
        ]

        if skill_type not in allowed_types:

            messages.error(
                request,
                'Invalid skill type selected.'
            )

            return redirect('manage_skills')

        skill = get_object_or_404(
            Skill,
            id=skill_id
        )

        existing_skill = StudentSkill.objects.filter(
            student=student,
            skill=skill,
            skill_type=skill_type
        ).exists()

        if existing_skill:

            messages.warning(
                request,
                'You have already added this skill.'
            )

            return redirect('manage_skills')

        StudentSkill.objects.create(
            student=student,
            skill=skill,
            skill_type=skill_type
        )

        messages.success(
            request,
            'Skill added successfully!'
        )

        return redirect('manage_skills')

    student_skills = StudentSkill.objects.filter(
        student=student
    )

    return render(request, 'manage_skills.html', {
        'student': student,
        'skills': skills,
        'student_skills': student_skills,
    })


@login_required
def remove_skill(request, skill_id):

    if request.method != 'POST':

        messages.error(
            request,
            'Invalid request method.'
        )

        return redirect('manage_skills')

    student = request.user.student_profile

    student_skill = get_object_or_404(
        StudentSkill,
        id=skill_id,
        student=student
    )

    student_skill.delete()

    messages.success(
        request,
        'Skill removed successfully!'
    )

    return redirect('manage_skills')


@login_required
def send_learning_request(request, student_id, skill_id):

    if request.method != 'POST':

        messages.error(
            request,
            'Invalid request method.'
        )

        return redirect('explore')

    sender = request.user.student_profile

    receiver = get_object_or_404(
        Student,
        id=student_id
    )

    skill = get_object_or_404(
        Skill,
        id=skill_id
    )

    if sender == receiver:

        messages.error(
            request,
            'You cannot send a learning request to yourself.'
        )

        return redirect('explore')

    teaches_skill = StudentSkill.objects.filter(
        student=receiver,
        skill=skill,
        skill_type='teach'
    ).exists()

    if not teaches_skill:

        messages.error(
            request,
            'This student does not teach this skill.'
        )

        return redirect('explore')

    existing_request = LearningRequest.objects.filter(
        sender=sender,
        receiver=receiver,
        skill=skill,
        status='pending'
    ).exists()

    if existing_request:

        messages.warning(
            request,
            'You already have a pending request for this skill.'
        )

        return redirect('explore')

    LearningRequest.objects.create(
        sender=sender,
        receiver=receiver,
        skill=skill,
        status='pending'
    )

    notification_message = (
        f'{sender.name} sent you a learning request '
        f'for {skill.name}.'
    )

    Notification.objects.create(
        student=receiver,
        message=notification_message
    )

    send_realtime_notification(
        receiver,
        notification_message
    )

    messages.success(
        request,
        f'Learning request sent to {receiver.name}!'
    )

    return redirect('explore')


@login_required
def requests(request):

    student = request.user.student_profile

    received_requests = LearningRequest.objects.filter(
        receiver=student
    ).select_related(
        'sender',
        'skill'
    ).order_by('-created_at')

    sent_requests = LearningRequest.objects.filter(
        sender=student
    ).select_related(
        'receiver',
        'skill'
    ).order_by('-created_at')

    return render(request, 'requests.html', {
        'received_requests': received_requests,
        'sent_requests': sent_requests,
    })


@login_required
def accept_request(request, request_id):

    if request.method != 'POST':

        messages.error(
            request,
            'Invalid request method.'
        )

        return redirect('requests')

    student = request.user.student_profile

    learning_request = get_object_or_404(
        LearningRequest,
        id=request_id,
        receiver=student
    )

    if learning_request.status != 'pending':

        messages.warning(
            request,
            'This learning request has already been processed.'
        )

        return redirect('requests')

    learning_request.status = 'accepted'
    learning_request.save()

    notification_message = (
        f'{student.name} accepted your learning request '
        f'for {learning_request.skill.name}.'
    )

    Notification.objects.create(
        student=learning_request.sender,
        message=notification_message
    )

    send_realtime_notification(
        learning_request.sender,
        notification_message
    )

    messages.success(
        request,
        f'Learning request from {learning_request.sender.name} accepted!'
    )

    return redirect('requests')


@login_required
def reject_request(request, request_id):

    if request.method != 'POST':

        messages.error(
            request,
            'Invalid request method.'
        )

        return redirect('requests')

    student = request.user.student_profile

    learning_request = get_object_or_404(
        LearningRequest,
        id=request_id,
        receiver=student
    )

    if learning_request.status != 'pending':

        messages.warning(
            request,
            'This learning request has already been processed.'
        )

        return redirect('requests')

    learning_request.status = 'rejected'
    learning_request.save()

    notification_message = (
        f'{student.name} rejected your learning request '
        f'for {learning_request.skill.name}.'
    )

    Notification.objects.create(
        student=learning_request.sender,
        message=notification_message
    )

    send_realtime_notification(
        learning_request.sender,
        notification_message
    )

    messages.success(
        request,
        f'Learning request from {learning_request.sender.name} rejected.'
    )

    return redirect('requests')


@login_required
def submit_review(request, student_id):

    reviewer = request.user.student_profile

    reviewed_student = get_object_or_404(
        Student,
        id=student_id
    )

    if reviewer == reviewed_student:

        messages.error(
            request,
            'You cannot review yourself.'
        )

        return redirect('profile')

    accepted_exchange = LearningRequest.objects.filter(
        sender=reviewer,
        receiver=reviewed_student,
        status='accepted'
    ).exists()

    if not accepted_exchange:

        messages.error(
            request,
            'You can review a student only after an accepted exchange.'
        )

        return redirect('profile')

    existing_review = Review.objects.filter(
        reviewer=reviewer,
        reviewed_student=reviewed_student
    ).exists()

    if existing_review:

        messages.warning(
            request,
            'You have already reviewed this student.'
        )

        return redirect('profile')

    if request.method == 'POST':

        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        try:
            rating = int(rating)
        except (TypeError, ValueError):

            messages.error(
                request,
                'Please select a valid rating.'
            )

            return redirect('profile')

        if rating < 1 or rating > 5:

            messages.error(
                request,
                'Rating must be between 1 and 5.'
            )

            return redirect('profile')

        if not comment or not comment.strip():

            messages.error(
                request,
                'Please enter a comment.'
            )

            return redirect('profile')

        Review.objects.create(
            reviewer=reviewer,
            reviewed_student=reviewed_student,
            rating=rating,
            comment=comment.strip()
        )

        notification_message = (
            f'{reviewer.name} reviewed your SkillSwap profile.'
        )

        Notification.objects.create(
            student=reviewed_student,
            message=notification_message
        )

        send_realtime_notification(
            reviewed_student,
            notification_message
        )

        messages.success(
            request,
            f'Your review for {reviewed_student.name} was submitted successfully!'
        )

        return redirect('profile')

    return render(request, 'submit_review.html', {
        'reviewed_student': reviewed_student,
    })


@login_required
def mark_notification_read(request, notification_id):

    if request.method != 'POST':

        messages.error(
            request,
            'Invalid request method.'
        )

        return redirect('dashboard')

    student = request.user.student_profile

    notification = get_object_or_404(
        Notification,
        id=notification_id,
        student=student
    )

    notification.is_read = True

    notification.save()

    return redirect('dashboard')


@login_required
def logout_view(request):

    if request.method != 'POST':

        messages.error(
            request,
            'Invalid request method.'
        )

        return redirect('dashboard')

    logout(request)

    messages.success(
        request,
        'You have been logged out successfully.'
    )

    return redirect('home')