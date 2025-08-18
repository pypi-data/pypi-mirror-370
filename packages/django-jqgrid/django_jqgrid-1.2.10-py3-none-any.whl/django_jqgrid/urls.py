from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter

from django_jqgrid.views import GridFilterViewSet

router = DefaultRouter()
router.register(r'grid-filter', GridFilterViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Example page showcasing standalone grid
    path('example/', TemplateView.as_view(template_name='django_jqgrid/example_page.html'), name='jqgrid_example'),
]
