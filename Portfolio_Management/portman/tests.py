# from django.test import TestCase

# # Create your tests here.


from django.contrib.auth.hashers import check_password
from django.conf import settings
settings.configure(DEFAULT_SETTINGS_MODULE="Portfolio Management.settings")


# Example hashed password
hashed_password = "pbkdf2_sha256$870000$UgvNP51IAjEQkv45AULlwP$lOQsDXRkaTrmWRKwdZTI/Uvfks5M7A5Oa2OzNGdU5ms="

# Check if the password matches
is_correct = check_password('Naveenrwt012@#', hashed_password)

print(is_correct)  # True if the password is correct, False otherwise
