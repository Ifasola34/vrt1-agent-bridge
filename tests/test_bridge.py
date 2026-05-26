"""Tests for the core bridge logic."""

import pytest

from veritas.attestation import sign_attestation, make_attestation
from veritas.crypto import OracleKey

from vrt1_agent_bridge import import_attestation, import_batch, AttestationImport


class TestImportAttestation:
    def test_produces_signed_action(self, sample_attestation, oracle_key):
        result = import_attestation(sample_attestation, oracle_key)
        assert isinstance(result, AttestationImport)
        assert result.signed_action.verify()

    def test_action_type_is_infer(self, sample_attestation, oracle_key):
        result = import_attestation(sample_attestation, oracle_key)
        assert result.signed_action.action.action_type == "infer"

    def test_agent_matches_oracle(self, sample_attestation, oracle_key):
        result = import_attestation(sample_attestation, oracle_key)
        assert result.signed_action.action.agent == oracle_key.xonly_pubkey_hex

    def test_target_is_model(self, sample_attestation, oracle_key):
        result = import_attestation(sample_attestation, oracle_key)
        assert result.signed_action.action.target == "veritas.sentiment.keyword.v1"

    def test_params_contain_input_hash(self, sample_attestation, oracle_key):
        result = import_attestation(sample_attestation, oracle_key)
        params = result.signed_action.action.params
        assert params["input_hash"] == "ab" * 32

    def test_params_contain_epoch(self, sample_attestation, oracle_key):
        result = import_attestation(sample_attestation, oracle_key)
        params = result.signed_action.action.params
        assert params["epoch"] == 7

    def test_params_contain_attestation_sig(self, sample_attestation, oracle_key):
        result = import_attestation(sample_attestation, oracle_key)
        params = result.signed_action.action.params
        assert params["attestation_sig"] == sample_attestation.sig

    def test_outcome_preserves_dict_output(self, sample_attestation, oracle_key):
        result = import_attestation(sample_attestation, oracle_key)
        outcome = result.signed_action.action.outcome
        assert outcome == {"label": "bullish", "score": 0.42}

    def test_outcome_wraps_non_dict_output(self, oracle_key):
        att = make_attestation(
            model="test.v1",
            input_hash="cc" * 32,
            output="raw string result",
            epoch=1,
            oracle_pubkey_hex=oracle_key.xonly_pubkey_hex,
            ts=1700000000,
        )
        signed = sign_attestation(att, oracle_key)
        result = import_attestation(signed, oracle_key)
        assert result.signed_action.action.outcome == {"output": "raw string result"}

    def test_outcome_wraps_list_output(self, oracle_key):
        att = make_attestation(
            model="test.v1",
            input_hash="dd" * 32,
            output=[1, 2, 3],
            epoch=1,
            oracle_pubkey_hex=oracle_key.xonly_pubkey_hex,
            ts=1700000000,
        )
        signed = sign_attestation(att, oracle_key)
        result = import_attestation(signed, oracle_key)
        assert result.signed_action.action.outcome == {"output": [1, 2, 3]}

    def test_timestamp_preserved(self, sample_attestation, oracle_key):
        result = import_attestation(sample_attestation, oracle_key)
        assert result.signed_action.action.ts == 1700000000

    def test_source_reference_kept(self, sample_attestation, oracle_key):
        result = import_attestation(sample_attestation, oracle_key)
        assert result.source_attestation is sample_attestation

    def test_wrong_key_raises(self, sample_attestation, other_key):
        with pytest.raises(ValueError, match="does not match"):
            import_attestation(sample_attestation, other_key)

    def test_invalid_sig_raises(self, oracle_key):
        att = make_attestation(
            model="test.v1",
            input_hash="ee" * 32,
            output={"x": 1},
            epoch=1,
            oracle_pubkey_hex=oracle_key.xonly_pubkey_hex,
            ts=1700000000,
        )
        from veritas.attestation import SignedAttestation
        tampered = SignedAttestation(attestation=att, sig="ff" * 64)
        with pytest.raises(ValueError, match="invalid signature"):
            import_attestation(tampered, oracle_key)

    def test_skip_verification(self, oracle_key):
        att = make_attestation(
            model="test.v1",
            input_hash="ee" * 32,
            output={"x": 1},
            epoch=1,
            oracle_pubkey_hex=oracle_key.xonly_pubkey_hex,
            ts=1700000000,
        )
        from veritas.attestation import SignedAttestation
        tampered = SignedAttestation(attestation=att, sig="ff" * 64)
        result = import_attestation(tampered, oracle_key, verify_source=False)
        assert result.signed_action.action.action_type == "infer"

    def test_action_id_deterministic(self, sample_attestation, oracle_key):
        r1 = import_attestation(sample_attestation, oracle_key)
        r2 = import_attestation(sample_attestation, oracle_key)
        assert r1.signed_action.id == r2.signed_action.id

    def test_different_attestations_different_ids(self, sample_attestations, oracle_key):
        r1 = import_attestation(sample_attestations[0], oracle_key)
        r2 = import_attestation(sample_attestations[1], oracle_key)
        assert r1.signed_action.id != r2.signed_action.id


class TestImportBatch:
    def test_imports_multiple(self, sample_attestations, oracle_key):
        results = import_batch(sample_attestations, oracle_key)
        assert len(results) == 5
        for r in results:
            assert r.signed_action.verify()

    def test_empty_list_raises(self, oracle_key):
        with pytest.raises(ValueError, match="empty"):
            import_batch([], oracle_key)

    def test_preserves_order(self, sample_attestations, oracle_key):
        results = import_batch(sample_attestations, oracle_key)
        for i, r in enumerate(results):
            assert r.signed_action.action.params["epoch"] == i

    def test_all_actions_are_infer(self, sample_attestations, oracle_key):
        results = import_batch(sample_attestations, oracle_key)
        for r in results:
            assert r.signed_action.action.action_type == "infer"
