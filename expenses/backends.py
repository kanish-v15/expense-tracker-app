"""Backends.py"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

class EmailBackend(ModelBackend):
    """email backend"""
    def authenticate(self, request, username=None, password=None, **kwargs):
        usermodel = get_user_model()
        try:
            user = usermodel.objects.get(Q(username__iexact=username) | Q(email__iexact=username))
        except usermodel.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None
