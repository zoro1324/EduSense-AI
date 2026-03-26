from datetime import date

from django.db.models import Avg, Max, Min
from rest_framework import status
from rest_framework.views import APIView

from api.models import EngagementLog, PeriodEngagementSummary
from api.serializers import EngagementLogSerializer, PeriodEngagementSummarySerializer
from api.views import error_response, success_response


class EngagementLogCreateView(APIView):
    def post(self, request):
        try:
            serializer = EngagementLogSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return success_response(serializer.data, status.HTTP_201_CREATED)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class EngagementLogsView(APIView):
    def get(self, request):
        try:
            logs = EngagementLog.objects.all().order_by("-timestamp")
            return success_response(EngagementLogSerializer(logs, many=True).data)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


class EngagementTodayView(APIView):
    def get(self, request):
        try:
            logs = EngagementLog.objects.filter(date=date.today()).order_by("period", "timestamp")
            return success_response(EngagementLogSerializer(logs, many=True).data)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


class EngagementHistoryView(APIView):
    def get(self, request):
        try:
            class_name = request.query_params.get("class_name")
            queryset = EngagementLog.objects.all().order_by("-date", "period")
            if class_name:
                queryset = queryset.filter(class_name=class_name)
            return success_response(EngagementLogSerializer(queryset, many=True).data)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


class EngagementHeatmapView(APIView):
    def get(self, request):
        try:
            data = (
                EngagementLog.objects.values("date", "period")
                .annotate(avg_percent=Avg("engagement_percent"), min_percent=Min("engagement_percent"), max_percent=Max("engagement_percent"))
                .order_by("date", "period")
            )
            summaries = []
            for item in data:
                summary, _ = PeriodEngagementSummary.objects.update_or_create(
                    class_name=request.query_params.get("class_name", "ALL"),
                    date=item["date"],
                    period=item["period"],
                    defaults={
                        "avg_engagement_percent": item["avg_percent"],
                        "min_engagement_percent": item["min_percent"],
                        "max_engagement_percent": item["max_percent"],
                        "dead_period_flag": item["avg_percent"] < 40,
                    },
                )
                summaries.append(summary)
            return success_response(PeriodEngagementSummarySerializer(summaries, many=True).data)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)
