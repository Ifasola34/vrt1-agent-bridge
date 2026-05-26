"""Core bridge: VERITAS SignedAttestation → vrt1-agents SignedAction."""

from __future__ import annotations

from dataclasses import dataclass

from veritas.attestation import SignedAttestation
from veritas.crypto import OracleKey
from vrt1_agents.action import AgentAction, SignedAction, make_action, sign_action


@dataclass(frozen=True)
class AttestationImport:
    signed_action: SignedAction
    source_attestation: SignedAttestation


def import_attestation(
    signed_att: SignedAttestation,
    key: OracleKey,
    *,
    verify_source: bool = True,
) -> AttestationImport:
    """Convert a VERITAS inference attestation into a signed agent action.

    The oracle that produced the attestation becomes the agent. The same key
    signs both the original attestation and the new agent action, providing
    cryptographic continuity.

    Args:
        signed_att: A signed VERITAS attestation to import.
        key: The oracle's key (must match attestation.oracle).
        verify_source: If True, verify the attestation signature before import.

    Returns:
        AttestationImport with the new SignedAction and source reference.

    Raises:
        ValueError: If key doesn't match oracle, or attestation sig is invalid.
    """
    att = signed_att.attestation

    if att.oracle != key.xonly_pubkey_hex:
        raise ValueError("key does not match attestation oracle")

    if verify_source and not signed_att.verify():
        raise ValueError("source attestation has invalid signature")

    action = make_action(
        agent_pubkey_hex=att.oracle,
        action_type="infer",
        target=att.model,
        params={
            "input_hash": att.input_hash,
            "epoch": att.epoch,
            "model": att.model,
            "attestation_sig": signed_att.sig,
        },
        outcome=_normalize_outcome(att.output),
        ts=att.ts,
    )

    signed = sign_action(action, key)
    return AttestationImport(signed_action=signed, source_attestation=signed_att)


def import_batch(
    attestations: list[SignedAttestation],
    key: OracleKey,
    *,
    verify_source: bool = True,
) -> list[AttestationImport]:
    """Import multiple attestations in batch.

    All attestations must be from the same oracle (matching key).
    """
    if not attestations:
        raise ValueError("cannot import empty attestation list")
    return [
        import_attestation(att, key, verify_source=verify_source)
        for att in attestations
    ]


def _normalize_outcome(output) -> dict:
    """Ensure output is wrapped in a dict for AgentAction.outcome."""
    if isinstance(output, dict):
        return output
    return {"output": output}
