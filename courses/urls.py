from django.urls import path, include
from rest_framework.routers import DefaultRouter

from courses.views import CourseViewSet, LessonViewSet


router = DefaultRouter()
router.register('', CourseViewSet)
router.register('lessons', LessonViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
