from django.db import models


class County(models.Model):
    county_code = models.CharField(primary_key=True, max_length=6)
    name = models.CharField(max_length=64)
    province = models.CharField(max_length=64, blank=True)
    prefecture = models.CharField(max_length=64, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    region_tag = models.CharField(max_length=16, blank=True)
    is_target = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["province", "prefecture", "name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.county_code})"


class CountyStatistic(models.Model):
    county = models.ForeignKey(County, on_delete=models.CASCADE, related_name="statistics")
    year = models.PositiveIntegerField()
    payload = models.JSONField()

    class Meta:
        unique_together = ("county", "year")
        ordering = ["county__county_code", "-year"]

    def __str__(self) -> str:
        return f"{self.county_id}-{self.year}"


class Surveyor(models.Model):
    surveyor_id = models.CharField(primary_key=True, max_length=16)
    name = models.CharField(max_length=32)
    gender = models.CharField(max_length=8, blank=True)
    school = models.CharField(max_length=64, blank=True)
    education_level = models.CharField(max_length=32, blank=True)
    major = models.CharField(max_length=64, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True)
    team_id = models.CharField(max_length=16, blank=True)
    primary_county = models.ForeignKey(
        County, on_delete=models.SET_NULL, null=True, blank=True, related_name="primary_surveyors"
    )
    role = models.CharField(max_length=32, blank=True)
    batch_label = models.CharField(max_length=32, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    interview_completed = models.PositiveIntegerField(default=0)
    interview_pending = models.PositiveIntegerField(default=0)
    expertise = models.TextField(blank=True)
    training_completed = models.BooleanField(default=False)
    equipment_status = models.CharField(max_length=32, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["surveyor_id"]

    def __str__(self) -> str:
        return f"{self.surveyor_id} - {self.name}"


class Interview(models.Model):
    interview_id = models.CharField(primary_key=True, max_length=16)
    surveyor = models.ForeignKey(Surveyor, on_delete=models.SET_NULL, null=True, related_name="interviews")
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name="interviews")
    interviewee_id = models.CharField(max_length=32, blank=True)
    interviewee_name = models.CharField(max_length=32, blank=True)
    interviewee_profile = models.TextField(blank=True)
    transcript = models.TextField()
    interview_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=128, blank=True)
    quality_score = models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-interview_date", "interview_id"]

    def __str__(self) -> str:
        return self.interview_id
