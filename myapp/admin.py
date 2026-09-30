from django.contrib import admin
from .models import (
    Student,
    Skill,
    StudentSkill,
    LearningRequest,
    Review,
    Notification
)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'department', 'year')
    search_fields = ('name', 'user__username', 'department')
    list_filter = ('department', 'year')


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(StudentSkill)
class StudentSkillAdmin(admin.ModelAdmin):
    list_display = ('student', 'skill', 'skill_type')
    search_fields = ('student__name', 'skill__name')
    list_filter = ('skill_type',)


@admin.register(LearningRequest)
class LearningRequestAdmin(admin.ModelAdmin):
    list_display = (
        'sender',
        'receiver',
        'skill',
        'status',
        'created_at'
    )
    search_fields = (
        'sender__name',
        'receiver__name',
        'skill__name'
    )
    list_filter = ('status', 'created_at')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'reviewer',
        'reviewed_student',
        'rating',
        'created_at'
    )
    search_fields = (
        'reviewer__name',
        'reviewed_student__name',
        'comment'
    )
    list_filter = ('rating', 'created_at')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'message',
        'is_read',
        'created_at'
    )
    search_fields = (
        'student__name',
        'message'
    )
    list_filter = ('is_read', 'created_at')


admin.site.site_header = 'SkillSwap Administration'
admin.site.site_title = 'SkillSwap Admin'
admin.site.index_title = 'SkillSwap Campus Management'