import hashlib

def seed_from_string(seed_str):
    """
    Convierte una cadena alfanumérica en un número entero reproducible para usar con random.seed().
    """
    return int(hashlib.sha256(seed_str.encode('utf-8')).hexdigest(), 16) % (2**32)