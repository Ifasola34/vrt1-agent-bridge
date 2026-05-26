"""Nostr kind-1990 wrapping for bridged actions."""

from __future__ import annotations

from veritas.crypto import OracleKey
from vrt1_agents.action import SignedAction
from vrt1_agents.nostr import NostrEvent, build_action_event

from .bridge import AttestationImport


def wrap_as_event(
    imported: AttestationImport,
    key: OracleKey,
) -> NostrEvent:
    """Wrap an imported attestation as a Nostr kind-1990 event.

    The event is double-signed: the inner SignedAction has its own
    BIP-340 Schnorr signature, and the outer Nostr event adds a second
    signature over the event ID (defense in depth).
    """
    return build_action_event(imported.signed_action, key)
