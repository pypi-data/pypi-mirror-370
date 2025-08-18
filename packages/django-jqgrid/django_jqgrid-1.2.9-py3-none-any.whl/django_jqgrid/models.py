from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import models

User = get_user_model()


class GridFilter(models.Model):
    """
    Model to store grid filters that can be user-specific or global
    This replaces the dependency on UserSpecificConfig from mainapp
    """
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=100, default='tmplFilters')
    value = models.JSONField(default=dict)
    table = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                   related_name='grid_filters')
    is_global = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Grid Filter"
        verbose_name_plural = "Grid Filters"
        ordering = ['-created_at']

    # def __str__(self):
    #     return f"{self.name}"
