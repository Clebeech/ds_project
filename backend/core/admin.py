from django.contrib import admin

from .models import County, CountyStatistic, Interview, Surveyor


@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ("county_code", "name", "province", "prefecture", "is_target")
    search_fields = ("county_code", "name", "prefecture", "province")
    list_filter = ("province", "is_target")


@admin.register(CountyStatistic)
class CountyStatisticAdmin(admin.ModelAdmin):
    list_display = ("county", "year")
    list_filter = ("year", "county__province")
    search_fields = ("county__county_code", "county__name")


@admin.register(Surveyor)
class SurveyorAdmin(admin.ModelAdmin):
    list_display = ("surveyor_id", "name", "team_id", "primary_county", "training_completed")
    search_fields = ("surveyor_id", "name", "team_id")
    list_filter = ("training_completed", "role")


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ("interview_id", "county", "surveyor", "interview_date", "quality_score")
    list_filter = ("interview_date", "quality_score", "county__province")
    search_fields = ("interview_id", "interviewee_name", "county__name", "surveyor__surveyor_id")
