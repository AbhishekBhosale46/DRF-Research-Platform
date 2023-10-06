from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


""" Manager for users """
class UserManager(BaseUserManager):
    
    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user"""
        if not email:
            raise ValueError('User must have an email')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """Create and return new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


""" Custom user model """
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email


class Domain(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Opportunity_Type(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    
class User_Profile(models.Model):
    # ROLE_CHOICES = [
    #     ("S", "Student"),
    #     ("P", "Professor"),
    #     ("O", "Other"),
    # ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=15)
    about = models.TextField()
    contact_no = models.IntegerField(blank=True)
    contact_email = models.EmailField()
    domains = models.ManyToManyField(Domain)
    skills = models.ManyToManyField(Skill)

    def __str__(self):
        return self.user.email


class Opportunity(models.Model):
    title = models.TextField()
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    duration = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    domains = models.ManyToManyField(Domain)
    skills = models.ManyToManyField(Skill)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.start_date and self.end_date:
            self.duration = (self.end_date-self.start_date).days
        else:
            self.duration = None
        super().save(*args, **kwargs)


class Application(models.Model):
    STATUS_CHOICES = [
        ("P", "Pending"),
        ("A", "Accepted"),
        ("R", "Rejected"),
    ]
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="P")
    created_at = models.DateTimeField(auto_now_add=True)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id} {self.applicant} {self.opportunity}"



    

