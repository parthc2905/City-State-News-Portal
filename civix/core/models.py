from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from location.models import State, City

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_admin', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_admin') is not True:
            raise ValueError('Superuser must have is_admin=True.')

        return self.create_user(email, password, **extra_fields)

# Create your models here.
class User(AbstractBaseUser):

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin
        
    # we will use email as the unique identifier for authentication instead of username
    first_name = models.CharField(max_length=50,null=True)
    middle_name = models.CharField(max_length=50,null=True)
    last_name = models.CharField(max_length=50,null=True)
    email = models.EmailField(unique=True)
    role_choice =(
        ('admin','admin'),
        ('reader','reader'),
        ('journalist','journalist'),
        ('advertiser','advertiser'),
    )
    role = models.CharField(max_length=10,choices=role_choice, default='reader')
    phone = models.CharField(max_length=15, null=True)
    acc_choice = (
        ('active','active'),
        ('blocked','blocked'),
        ('suspended','suspended'),
    )
    account_status = models.CharField(max_length=10,choices=acc_choice, default='active')
    app_choice = (
        ('pending','pending'),
        ('approved','approved'),
        ('rejected','rejected'),
        ('not_required','not_required'),
    )
    approval_status = models.CharField(max_length=15,choices=app_choice, default='pending')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    objects = UserManager()

    #override userName field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta: 
        db_table = "users"
    
    def __str__(self):
        return self.email

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    profile_image = models.CharField(max_length=255, null=True)
    
    # Notification & Newsletter Settings
    email_notifications = models.BooleanField(default=True, help_text="Receive email updates about new articles in your city")
    breaking_news_alerts = models.BooleanField(default=True, help_text="Get instant notifications for breaking news")
    weekly_newsletter = models.BooleanField(default=True, help_text="Receive a weekly digest of top stories")
    article_recommendations = models.BooleanField(default=True, help_text="Article Recommendations")

    class Meta:
        db_table = "profile"

    def __str__(self):
        return f"{self.user.email}'s Profile"