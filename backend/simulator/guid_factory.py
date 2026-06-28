import uuid

NAMESPACE = uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")


def generate_guid(entity_type: str, index: int, seed: str = "default") -> str:
    key = f"{seed}:{entity_type}:{index}"
    return str(uuid.uuid5(NAMESPACE, key))
