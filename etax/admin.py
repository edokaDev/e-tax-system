from django.contrib import admin
from .models import User, Address, Tcc, TaxPayment, Asset, AssetType

# Register your models here.

admin.site.register(User)
admin.site.register(Address)
admin.site.register(Tcc)
admin.site.register(TaxPayment)
admin.site.register(Asset)
admin.site.register(AssetType)
