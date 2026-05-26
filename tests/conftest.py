"""Shared fixtures for vrt1-agent-bridge tests."""

import pytest

from veritas.attestation import Attestation, SignedAttestation, sign_attestation, make_attestation
from veritas.crypto import OracleKey


@pytest.fixture
def oracle_key():
    return OracleKey.from_hex("1111111111111111111111111111111111111111111111111111111111111111")


@pytest.fixture
def other_key():
    return OracleKey.from_hex("2222222222222222222222222222222222222222222222222222222222222222")


@pytest.fixture
def sample_attestation(oracle_key):
    att = make_attestation(
        model="veritas.sentiment.keyword.v1",
        input_hash="ab" * 32,
        output={"label": "bullish", "score": 0.42},
        epoch=7,
        oracle_pubkey_hex=oracle_key.xonly_pubkey_hex,
        ts=1700000000,
    )
    return sign_attestation(att, oracle_key)


@pytest.fixture
def sample_attestations(oracle_key):
    results = []
    for i in range(5):
        att = make_attestation(
            model=f"veritas.test.v{i}",
            input_hash=f"{i:02x}" * 32,
            output={"idx": i, "value": i * 0.1},
            epoch=i,
            oracle_pubkey_hex=oracle_key.xonly_pubkey_hex,
            ts=1700000000 + i * 60,
        )
        results.append(sign_attestation(att, oracle_key))
    return results
