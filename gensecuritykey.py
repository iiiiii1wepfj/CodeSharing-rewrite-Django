from django.core.management.utils import get_random_secret_key
secretkey = get_random_secret_key()
print(secretkey)