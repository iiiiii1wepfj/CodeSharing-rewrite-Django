import secrets
import string


def grnd(strlen):
    alphabet = string.ascii_letters + string.digits
    password = "".join(secrets.choice(alphabet) for i in range(strlen))
    return password
