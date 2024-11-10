"""Models.py"""
from django.db import models
from django.contrib.auth.models import User

class Expense(models.Model):
    """Expense Model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()

    def __str__(self):
        return f"{self.category} - {self.amount}"

class Category(models.Model):
    """Category Model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        """Makes unique categories"""
        unique_together = ['user', 'name']

    def __str__(self):
        return self.name
