from .settings import DEFAULTS
from typing import Any
import pickle
import sys
import unicodedata
import re

def build_proc_qs(
    qs,
    related_field: str | None,
    only_fields: tuple[str] | None,
    fields: tuple[str] | None,
    decrypt: bool
) -> Any:
    """
    Optimize queryset fetching:
      - select_related for single-valued relations (FK/OneToOne)
      - .only(...) on the correct model path
      - Always includes base 'pk'
    """
    
    def prepend_related(names: tuple[str]) -> tuple[str]:
        """
        Combines a related field path with a target field name to produce a fully qualified field reference.
        (e.g., "order__client__name").
        """
        return (f"{related_field}__{f}" for f in names) if related_field else names

    if related_field:
        qs = qs.select_related(related_field)

    if decrypt:
        target_fields = prepend_related(fields or ())
        qs = qs.values_list("pk", *target_fields)
        
    elif only_fields:
        target_fields = prepend_related(only_fields)
        qs = qs.only("pk", *target_fields)

    return qs

def resolve_related_field(obj: Any, related_field: str | None) -> Any:
    """
    Loops through chained attributes using '__' as a delimiter.
    Ex.: resolve_related_field(obj, 'order__client') -> obj.order.client
    """
    if not related_field:
        return obj
    
    try:
        for attr in related_field.split('__'):
            obj = getattr(obj, attr)
        return obj
    except AttributeError as e:
        raise AttributeError(f"Failed to access attribute '{attr}' on object '{obj}': {e}")

def make_cache_key(
        model_label: str,
        qs_signature: str,
        search: str,
        fields: tuple[str],
        related_field: str | None
    ) -> str:
    """
    Generates a stable cache key for the combination of queryset, search and fields.
    """
    import hashlib
    base = f"{model_label}|{qs_signature}|{search}|{','.join(fields)}|{related_field or ''}"
    digest = hashlib.sha1(base.encode("utf-8")).hexdigest()
    return f"dds:{digest}"

def estimate_avg_obj_size(sample: Any, fallback: int) -> int:
    """
    Returns the average object size in bytes based on an average of 10 samples + a 50% safety margin.
    """
    sample_size: int = 10
    safety_margin: float = 1.5

    try:
        objs = set(sample[:sample_size])
        total_size = sum(sys.getsizeof(pickle.dumps(o, protocol=pickle.HIGHEST_PROTOCOL)) for o in objs)
        avg_size = total_size / len(objs)
        return int(avg_size * safety_margin)
    except Exception:
        return fallback

def compute_batch_size(available_bytes: int, avg_obj_size: int, max_batch_size: int) -> int:
    """
    Calculate the batch size based on the available memory and the size of each object.
    """
    if avg_obj_size <= 0:
        return DEFAULTS.MIN_BATCH_SIZE
    batch = available_bytes // avg_obj_size
    batch = max(batch, DEFAULTS.MIN_BATCH_SIZE)
    batch = min(batch, max_batch_size or DEFAULTS.MAX_BATCH_SIZE)
    return batch

def normalize_text(text: str) -> str:
    # remove accents
    text = unicodedata.normalize("NFD", text)
    text = text.encode("ascii", "ignore").decode("utf-8")
    # remove punctuation and special characters
    text = re.sub(r"[^\w\s]", "", text)
    # lowercase
    return text.lower()
