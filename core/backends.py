from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(Q(username__icontains=username) | Q(email__icontains=username))
        except UserModel.DoesNotExist:
            return None
        
        if user.check_password(password):
            return user
        return None