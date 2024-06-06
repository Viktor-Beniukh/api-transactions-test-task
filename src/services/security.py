import secrets

from passlib.context import CryptContext

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return bcrypt_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> str:
    return bcrypt_context.verify(plain_password, hashed_password)


def generate_admin_token() -> str:
    token_length = 32
    return secrets.token_hex(token_length)