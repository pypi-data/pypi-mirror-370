from django.contrib.auth.models import UserManager as DjangoUserManager

class UserManager(DjangoUserManager):
    def create_user(self, email, password, **extra_fields):
        print(email)
        email = self.normalize_email(email)
        username = email  # Store username separately
        print(extra_fields)
        user = super().create_user(username, email, password, **extra_fields)  # Pass username and email separately
        # Create profile and settings after user is saved
        from shared_models.users.models import UserProfile, UserSettings
        UserProfile.objects.create(user=user)
        UserSettings.objects.create(user=user)
        return user