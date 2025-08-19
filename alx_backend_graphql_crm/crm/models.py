from django.db import models

class CRMModel(models.Model):
    name = models.CharField(max_length=100, default='Hello, GraphQL!')

    def __str__(self):
        return self.name