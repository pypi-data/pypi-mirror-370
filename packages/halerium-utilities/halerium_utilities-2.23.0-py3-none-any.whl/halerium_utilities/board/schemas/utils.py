import uuid


def check_uuid4(s: str):
    try:
        uuid.UUID(s, version=4)
    except ValueError:
        raise ValueError('Invalid uuid')
    return s
