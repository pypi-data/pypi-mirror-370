from dataclasses import dataclass

@dataclass(frozen=True)
class Defaults:
    # Percentage of available memory target for batch loading
    MEMORY_FRACTION: float = 0.60
    # Size of chunk sent at a time to each worker
    IMAP_CHUNKSIZE: int = 10_240
    # Execution method: "processes" | "threads" | "sync"
    EXECUTOR: str = "processes"
    # Default cache timeout in seconds
    CACHE_TIMEOUT: int = 600
    # Estimated average size of each object, in bytes (fallback)
    AVG_OBJ_SIZE_FALLBACK: int = 4096
    # Security limits
    MIN_BATCH_SIZE: int = 1_000
    MAX_BATCH_SIZE: int = 1_000_000

DEFAULTS = Defaults()
