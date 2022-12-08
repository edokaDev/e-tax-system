import random
from django.db import models
from django.contrib.auth.models import AbstractUser, User


# Create your models here.

USER_TYPES = [
    ('IND', 'Individual'),
    ('BIZ', 'Business'),
]

ASSET_TYPES = [
    ('HSE', 'House'),
    ('VEH', 'Vehicle'),
]

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
    address = models.OneToOneField(Address, on_delete=models.CASCADE, null=True, blank=True)
    # admin
    is_active = models.BooleanField(default=True)
    # general
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.username

class Tcc(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    is_expired = models.BooleanField(default=False)
    request_date = models.DateTimeField(auto_now=True)
    start = models.DateField()
    end = models.DateField()

    @property
    def tcc_no(self):
        return f"TCC-00{self.pk}"

    def __str__(self):
        return self.tcc_no


class AssetType(models.Model):
    name = models.CharField(max_length=10, choices=ASSET_TYPES)
    rate = models.FloatField()

    def __str__(self):
        return self.name


class Asset(models.Model):
    description = models.CharField(max_length=50)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now=True)
    asset_type = models.ForeignKey(AssetType, on_delete=models.CASCADE)
    price = models.FloatField()
    tax_amount = models.FloatField()
    tax_paid = models.BooleanField(default=False)

    def __str__(self):
        return self.description
    
    @property
    def get_rate_percentage(self):
        return self.asset_type.rate * 100
    
    def save(self, *args, **kwargs):
        self.tax_amount = self.asset_type.rate * self.price
        super(Asset, self).save(*args, **kwargs)


class TaxPayment(models.Model):
    asset = models.OneToOneField(Asset, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    is_successful = models.BooleanField(default=False)
    reference_no = models.CharField(max_length=13)
    amount = models.FloatField()

    def generate_ref(self):
        ref = f'TX-{self.asset.asset_type}-'
        ref += f'{random.randrange(100000, 199999)}'
        check = TaxPayment.objects.filter(reference_no=ref)
        if len(check) > 0:
            return self.generate_ref()
        return ref
    
    def save(self, *args, **kwargs):
        self.reference_no = self.generate_ref()
        super(TaxPayment, self).save(*args, **kwargs)
        

    def __str__(self):
        return self.reference_no
