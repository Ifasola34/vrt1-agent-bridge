"""Bridge VERITAS inference attestations into vrt1-agents action format."""

from .bridge import (
    import_attestation,
    import_batch,
    AttestationImport,
)
from .nostr import wrap_as_event

__all__ = [
    "import_attestation",
    "import_batch",
    "AttestationImport",
    "wrap_as_event",
]
