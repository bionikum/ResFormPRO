from werkzeug.security import generate_password_hash

password = 'AdminPassword123!'
password_hash = generate_password_hash(password)
print(f'Password hash for "AdminPassword123!":')
print(f'{password_hash}')
