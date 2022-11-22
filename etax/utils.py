from hashlib import sha256
import random

from .models import User

def get_unique_tin():
    # generate a random 10 digit number starting with 1
    tin = random.randrange(1000000000, 1999999999)

    check = User.objects.filter(tin=f"{tin}")
    if len(check) > 0:
        return get_unique_tin()
    return f"{tin}"
