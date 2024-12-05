import re

password_pattern = re.compile(r"^(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).+$")


def validate_password(password: str):
    if not password_pattern.match(password):
        raise ValueError(
            "Password is not valid! The password must consist of at least one lowercase, "
            "uppercase letter, number and symbols."
        )
