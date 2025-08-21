import bcrypt

def GenEncryptedPassword(password:str) -> str:
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed_password.decode()