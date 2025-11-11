from django.db.models import Q
from django.views.generic import ListView

from .models import County, Interview, Surveyor


class InterviewListView(ListView):
    model = Interview
    template_name = "core/interview_list.html"
    context_object_name = "interviews"
    paginate_by = 20

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .select_related("county", "surveyor")
        )
        county_code = self.request.GET.get("county")
        surveyor_id = self.request.GET.get("surveyor")
        keyword = self.request.GET.get("keyword")
        min_quality = self.request.GET.get("min_quality")

        if county_code:
            qs = qs.filter(county__county_code=county_code)
        if surveyor_id:
            qs = qs.filter(surveyor__surveyor_id=surveyor_id)
        if keyword:
            qs = qs.filter(
                Q(interviewee_name__icontains=keyword)
                | Q(interviewee_profile__icontains=keyword)
                | Q(transcript__icontains=keyword)
            )
        if min_quality:
            try:
                qs = qs.filter(quality_score__gte=int(min_quality))
            except ValueError:
                pass
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["counties"] = County.objects.order_by("province", "name")
        context["surveyors"] = Surveyor.objects.order_by("surveyor_id")
        context["current_filters"] = {
            "county": self.request.GET.get("county", ""),
            "surveyor": self.request.GET.get("surveyor", ""),
            "keyword": self.request.GET.get("keyword", ""),
            "min_quality": self.request.GET.get("min_quality", ""),
        }
        return context
