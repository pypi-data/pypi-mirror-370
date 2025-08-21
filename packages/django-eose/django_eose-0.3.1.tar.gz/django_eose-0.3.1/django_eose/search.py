from functools import partial
from multiprocessing import cpu_count
from typing import Any
import psutil

from django.core.cache import cache
from django.utils.text import slugify

from .executors import get_executor
from .settings import DEFAULTS
from .processors import process_obj, process_values
from .utils import (
    build_proc_qs,
    make_cache_key,
    estimate_avg_obj_size,
    compute_batch_size,
    normalize_text
)

def search_queryset(
    search: str,
    queryset: Any,
    *,
    related_field: str | None = None,
    fields: tuple[str] | None = None,
    only_fields: tuple[str] | None = None,
    executor: str = DEFAULTS.EXECUTOR,        # "processes" | "threads" | "sync"
    cache_timeout: int = DEFAULTS.CACHE_TIMEOUT,
    imap_chunksize: int = DEFAULTS.IMAP_CHUNKSIZE,
    memory_fraction: float = DEFAULTS.MEMORY_FRACTION,
    avg_obj_size_bytes: int | None = None,
    max_workers: int | None = None,
    max_batch_size: int| None = None,
    decrypt: bool = False
):
    """
    Parallel search over a queryset, checking if `search` (lowercase) appears in the `fields`.

    - related_field: relation path (e.g., "order__client") or None to use the object itself.
    - fields: list of fields to inspect in the final object.
    - only_fields: list of fields to load via .only(...) to optimize I/O.
    - executor: "processes" (CPU-bound), "threads" (I/O-bound), or "sync".
    - cache_timeout: seconds to cache the found IDs. Default is 600 seconds.
    - imap_chunksize: chunk size per worker.
    - memory_fraction: fraction of memory available for batch sizing.
    - avg_obj_size_bytes: estimated average size per object; if None, it will be calculated automatically\
    or inferred with fallback.
    - max_workers: number of workers; if None, use cpu_count().
    - max_batch_size: maximum number of objects per batch. Will be automatically adjusted if it does not fit in memory.
    - decrypt: decrypts data using Fernet. Faster than using Getters in Django.
    """
    if not search:
        return queryset.none()

    search = normalize_text(search)

    # Sign the queryset for the cache key
    model = queryset.model
    model_label = f"{model._meta.app_label}.{model._meta.model_name}"
    qs_signature = str(queryset.query)
    cache_key = make_cache_key(model_label, qs_signature, slugify(search), tuple(fields), related_field)

    cached_ids = cache.get(cache_key)
    if cached_ids:
        return queryset.filter(pk__in=cached_ids)

    # Estimates available memory and batch size
    if memory_fraction > 0:
        try:
            mem = psutil.virtual_memory()
            available_bytes = int(mem.available * memory_fraction)
        except Exception:
            available_bytes = DEFAULTS.AVG_OBJ_SIZE_FALLBACK * DEFAULTS.MIN_BATCH_SIZE
    else:
        available_bytes = DEFAULTS.AVG_OBJ_SIZE_FALLBACK * DEFAULTS.MIN_BATCH_SIZE
    
    # Build optimized queryset BEFORE sampling and iteration
    proc_qs = build_proc_qs(queryset, related_field, only_fields, fields, decrypt)

    # Sample to estimate size
    avg_size = avg_obj_size_bytes or estimate_avg_obj_size(proc_qs, DEFAULTS.AVG_OBJ_SIZE_FALLBACK)
    batch_size = compute_batch_size(available_bytes, avg_size, max_batch_size=max_batch_size)

    # Batch iteration
    total: int = queryset.count()
    matched_ids: set[int] = set()

    run = get_executor(executor)
    max_workers = max_workers or cpu_count()
    total_chunk = imap_chunksize * max_workers

    func = partial(
        process_values if decrypt else process_obj,
        search=search,
        related_field=related_field,
        fields=tuple(fields)
    )

    # Traverse the queryset in batches and parallelize per item
    for start in range(0, total, batch_size):
        batch_qs = proc_qs[start:start + batch_size]
        batch_iter = batch_qs.iterator(chunk_size=total_chunk)
        
        for result in run(batch_iter, func, chunksize=imap_chunksize, max_workers=max_workers):
            if result:
                matched_ids.add(result)

    cache.set(cache_key, set(matched_ids), timeout=cache_timeout)
    return queryset.filter(pk__in=matched_ids)
