# Create your views here.
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import JobRun
from .serializers import JobRunSerializer


class JobRunViewSet(ReadOnlyModelViewSet):
    queryset = JobRun.objects.all()
    serializer_class = JobRunSerializer
    permission_classes = [IsAdminUser]
