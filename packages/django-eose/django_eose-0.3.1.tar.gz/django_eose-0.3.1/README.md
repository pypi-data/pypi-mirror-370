# Django EOSE

**Django Encrypted Object Search Engine**  
An efficient search engine for encrypted fields in Django querysets, with support for parallel processing, smart batching, and result caching.

`django-eose` is ideal for scenarios where you need to search data that is encrypted in the database, providing high performance even on large datasets.

---

## Key Features

- **Parallel Search:** supports execution using processes, threads, or synchronous mode.  
- **Smart Batching:** batch size automatically adapts to available memory.  
- **Related Field Search:** search can be performed on fields of related objects, e.g., `order__client`.  
- **Result Caching:** frequently searched results are cached for faster repeated queries.  
- **Optimized for Large Datasets:** particularly useful for large datasets and encrypted fields.

---

## Installation

Install easily via `pip`:

```bash
pip install django-eose
```

## Requirements

- Python 3.10 or higher
- Django 5.2.5
- sqlparse==0.5.3
- asgiref==3.9.1
- psutil==7.0.0
- cffi==1.17.1
- cryptography==45.0.6
- pycparser==2.22

## Model Configuration

There are two ways to use django-eose. The first is to let django-eose handle the decryption itself using Fernet, which is much faster. The second is to create Getters in Django that already return the decrypted values. If you are going to use the first option, skip this step.

Example model using Fernet encryption:

```python
from django.db import models
from cryptography.fernet import Fernet

AES_KEY = b"<your_key_here>"

class Client(models.Model):
    _encrypted_name = models.BinaryField()
    _encrypted_email = models.BinaryField()

    # Method to decrypt
    def _decrypt_field(self, encrypted_value):
        return Fernet(AES_KEY).decrypt(encrypted_value).decode()

    # Method to encrypt
    def _encrypt_field(self, value):
        return Fernet(AES_KEY).encrypt(value.encode())
    
    # Creates properties that handle encryption/decryption
    @staticmethod
    def _property(field_name):
        def getter(self):
            return self._decrypt_field(getattr(self, field_name))
        
        def setter(self, value):
            setattr(self, field_name, self._encrypt_field(value))

        return property(getter, setter)
    
    # Fields accessible as normal attributes
    name = _property('_encrypted_name')
    email = _property('_encrypted_email')

```
⚠️ You interact with name and email like regular fields, while encryption/decryption happens transparently.

## Usage

Add AES_PASSWORD to your .env file:
```bash
AES_PASSWORD=your-password-here
```

To decrypt data in django-eose and speed up the process, use:

```python
from django_eose import search_queryset
from orders.models import OrderItem

# Example: search for "john" in related client fields
results = search_queryset(
    search="john",
    queryset=OrderItem.objects.all(),
    related_field="order__client",
    fields=("_encrypted_name", "_encrypted_email"),
    executor="processes",
    max_batch_size=1_000_000,
    decrypt=True
) # returns queryset.filter(pk__in=matched_ids)
```

To use the decrypted data returned by getters in Django, use:


```python
from django_eose import search_queryset
from orders.models import OrderItem

# Example: search for "john" in related client fields
results = search_queryset(
    search="john",
    queryset=OrderItem.objects.all(),
    related_field="order__client",
    fields=("name", "email"),
    only_fields=("_encrypted_name", "_encrypted_email"),
    executor="processes",
    max_batch_size=1_000_000
) # returns queryset.filter(pk__in=matched_ids)
```

## `search_queryset` Parameters

- search: search term (case-insensitive).
- queryset: Django queryset to search in.
- related_field: path to a related object using __ notation. (optional)
- fields: fields of the object to inspect.
- only_fields: fields to load with .only() for optimization (optional).
- executor: "processes", "threads", or "sync" (default: "processes").
- cache_timeout: cache duration in seconds (default: 600).
- imap_chunksize: chunk size per worker (default: 10240).
- memory_fraction: fraction of available memory for batching (default: 0.60).
- avg_obj_size_bytes: estimated average object size in bytes (optional).
- max_workers: maximum number of parallel workers (optional).
- max_batch_size: maximum number of objects per batch. (default: 1_000_000)
- decrypt: decrypt data using Fernet. (ignores the only_fields parameter)

Refer to `search_queryset` for full parameter details.

## Default Settings

`django-eose` defines default settings in `django_eose/settings.py`:

- MEMORY_FRACTION
- IMAP_CHUNKSIZE
- EXECUTOR
- CACHE_TIMEOUT
- AVG_OBJ_SIZE_FALLBACK
- MIN_BATCH_SIZE
- MAX_BATCH_SIZE

## License

MIT © 2025 Paulo Otávio Castoldi

## Links

[Source](https://github.com/paulootaviodev/django-eose)
