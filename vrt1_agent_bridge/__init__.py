"""Bridge VERITAS inference attestations into vrt1-agents action format."""

from .bridge import (
    import_attestation,
    import_batch,
    AttestationImport,
)
from .nostr import wrap_as_event
from .verify import verify_bridge_chain

__all__ = [
    "import_attestation",
    "import_batch",
    "AttestationImport",
    "wrap_as_event",
    "verify_bridge_chain",
]
