# Code Sharing

Rewrite of my asp.net project in Django.

To run this project it is necessary to go through these steps:
1. Generate a secret key:
    ```
    from django.core.management.utils import get_random_secret_key  
    secretkey = get_random_secret_key()
    print(secretkey)
    ```
    and replace the `SECRET_KEY` in `settings.py`.
2. Set debug to false in `settings.py`:
```
DEBUG = True
```
3. Change the name of `mailconfig.py.example` to `mailconfig.py` and change the values to your own mail.

## Credit
I did this project together with [iii123iii](https://github.com/iii123iii)