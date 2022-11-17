from django.db import models
from django.contrib.auth.models import AbstractUser, User


# Create your models here.

USER_TYPES = (
    ('IND', 'Individual'),
    ('BIZ', 'Business'),
)

ASSET_TYPES = (
    ('HSE', 'House'),
    ('VEH', 'Vehicle'),
)

class Address(models.Model):
    house_no = models.IntegerField()
    street = models.CharField(max_length=50)
    town = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.town}, Enugu State"


class User(AbstractUser):
    # payer
    tin = models.CharField(max_length=10, null=True, blank=True)
    user_type = models.CharField(max_length=50, choices=USER_TYPES)
    is_cleared = models.BooleanField(default=False) 
    is_payer = models.BooleanField(default=False)
    address = models.OneToOneField(Address, on_delete=models.CASCADE)
    # admin
    is_active = models.BooleanField(default=True)
    # general
    is_admin = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.first_name

class Tcc(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    is_expired = models.BooleanField(default=False)
    request_date = models.DateTimeField(auto_now=True)
    start = models.DateField()
    end = models.DateField()
    approver = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"TCC-00{self.pk}"

class Asset(models.Model):
    description = models.CharField(max_length=50)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now=True)
    asset_type = models.CharField(max_length=50, choices=ASSET_TYPES)

    def __str__(self):
        return self.description

class TaxPayment(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    is_successful = models.BooleanField(default=False)
    reference_no = models.CharField(max_length=10)

    def __str__(self):
        return self.reference_no