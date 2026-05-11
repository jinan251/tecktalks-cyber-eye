import bcrypt

def verify_password(password: str, hashed_password: str):
    return bcrypt.checkpw(
        password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )