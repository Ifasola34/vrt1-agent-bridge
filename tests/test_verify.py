"""Tests for bridge chain verification."""

import pytest

from veritas.attestation import SignedAttestation, make_attestation, sign_attestation
from veritas.crypto import OracleKey

from vrt1_agent_bridge import import_attestation
from vrt1_agent_bridge.verify import verify_bridge_chain


class TestVerifyBridgeChain:
    def test_valid_chain(self, sample_attestation, oracle_key):
        imported = import_attestation(sample_attestation, oracle_key)
        assert verify_bridge_chain(imported.signed_action, sample_attestation)

    def test_tampered_action_fails(self, sample_attestation, oracle_key):
        imported = import_attestation(sample_attestation, oracle_key)
        from vrt1_agents.action import SignedAction, AgentAction
        tampered_action = AgentAction(
            agent=imported.signed_action.action.agent,
            action_type="infer",
            target="tampered.model",
            params=imported.signed_action.action.params,
            outcome=imported.signed_action.action.outcome,
            ts=imported.signed_action.action.ts,
            parent_action=None,
            v=1,
        )
        tampered = SignedAction(action=tampered_action, sig=imported.signed_action.sig)
        assert not verify_bridge_chain(tampered, sample_attestation)

    def test_tampered_attestation_fails(self, sample_attestation, oracle_key):
        imported = import_attestation(sample_attestation, oracle_key)
        att = make_attestation(
            model="different.model",
            input_hash="ff" * 32,
            output={"x": 1},
            epoch=99,
            oracle_pubkey_hex=oracle_key.xonly_pubkey_hex,
            ts=1700000000,
        )
        fake_signed = SignedAttestation(attestation=att, sig="00" * 64)
        assert not verify_bridge_chain(imported.signed_action, fake_signed)

    def test_mismatched_oracle_fails(self, sample_attestation, oracle_key, other_key):
        imported = import_attestation(sample_attestation, oracle_key)
        other_att = make_attestation(
            model="test.v1",
            input_hash="aa" * 32,
            output={"v": 1},
            epoch=1,
            oracle_pubkey_hex=other_key.xonly_pubkey_hex,
            ts=1700000000,
        )
        other_signed = sign_attestation(other_att, other_key)
        assert not verify_bridge_chain(imported.signed_action, other_signed)

    def test_wrong_attestation_sig_in_params_fails(self, sample_attestation, oracle_key):
        imported = import_attestation(sample_attestation, oracle_key)
        other_att = make_attestation(
            model="veritas.sentiment.keyword.v1",
            input_hash="ab" * 32,
            output={"label": "bullish", "score": 0.42},
            epoch=7,
            oracle_pubkey_hex=oracle_key.xonly_pubkey_hex,
            ts=1700000001,
        )
        other_signed = sign_attestation(other_att, oracle_key)
        assert not verify_bridge_chain(imported.signed_action, other_signed)
