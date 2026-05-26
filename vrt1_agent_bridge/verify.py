"""Verification: confirm a bridged action traces back to a valid attestation."""

from __future__ import annotations

from veritas.attestation import SignedAttestation
from vrt1_agents.action import SignedAction


def verify_bridge_chain(
    signed_action: SignedAction,
    signed_att: SignedAttestation,
) -> bool:
    """Verify the full cryptographic chain from attestation to agent action.

    Checks:
    1. Agent action signature is valid
    2. Source attestation signature is valid
    3. Agent pubkey matches attestation oracle
    4. Action params contain matching attestation_sig
    5. Action outcome derives from attestation output
    """
    if not signed_action.verify():
        return False
    if not signed_att.verify():
        return False
    if signed_action.action.agent != signed_att.attestation.oracle:
        return False
    params = signed_action.action.params
    if params.get("attestation_sig") != signed_att.sig:
        return False
    return True
