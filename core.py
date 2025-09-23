import hashlib
import base64
import json
import math
from typing import List, Callable

def hash_sha256(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError("Entrada deve ser uma string.")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def normalize(values: List[float]) -> List[float]:
    if not values:
        raise ValueError("Lista vazia.")
    min_val, max_val = min(values), max(values)
    if min_val == max_val:
        return [0.0 for _ in values]
    return [(v - min_val) / (max_val - min_val) for v in values]

def jaccard_similarity(set_a: set, set_b: set) -> float:
    if not isinstance(set_a, set) or not isinstance(set_b, set):
        raise TypeError("Entradas devem ser conjuntos.")
    union = set_a | set_b
    if not union:
        return 0.0
    return len(set_a & set_b) / len(union)

def encode_base64(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError("Entrada deve ser uma string.")
    return base64.b64encode(text.encode("utf-8")).decode("utf-8")

def validate_json_structure(json_str: str, required_keys: List[str]) -> bool:
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        return False
    return all(key in data for key in required_keys)

def safe_execute(func: Callable, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        return f"Erro interno: {str(e)}"
