from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return str(password_context.hash(password))


def verify_password(plain_password: str, password_hash: str) -> bool:
    return bool(password_context.verify(plain_password, password_hash))
