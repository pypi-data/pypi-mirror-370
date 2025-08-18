from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import models
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from django_jqgrid.models import GridFilter
from django_jqgrid.serializers import GridFilterSerializer


class GridFilterViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing grid filters
    """
    queryset = GridFilter.objects.all()
    serializer_class = GridFilterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all filters for the currently authenticated user
        and any global filters.
        """
        user = self.request.user
        # Return both user-specific and global filters
        return GridFilter.objects.filter(
            # Filter for the current user's filters OR global filters
            models.Q(created_by=user) | models.Q(is_global=True)
        ).select_related('table').order_by('-created_at')

    @action(detail=False, methods=['get'])
    def by_table(self, request):
        """
        Return filters for a specific table (content type)
        """
        app_name = request.query_params.get('app_name')
        model_name = request.query_params.get('model')

        if not app_name or not model_name:
            return Response(
                {"error": "Both app_name and model parameters are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get content type for this app/model with caching
            cache_key = f"content_type_{app_name}_{model_name}"
            content_type = cache.get(cache_key)
            if not content_type:
                content_type = ContentType.objects.get(app_label=app_name, model=model_name)
                cache.set(cache_key, content_type, 3600)  # Cache for 1 hour

            # Get filters for this content type
            filters = self.get_queryset().filter(table=content_type)
            serializer = self.get_serializer(filters, many=True)

            return Response({
                "status": "success",
                "data": {
                    "content_type": {
                        "id": content_type.id,
                        "app_label": content_type.app_label,
                        "model": content_type.model
                    },
                    "filters": serializer.data
                }
            })
        except ContentType.DoesNotExist:
            return Response(
                {"error": f"Content type for {app_name}.{model_name} not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
