"""Tests for Nostr event wrapping."""

import pytest

from vrt1_agent_bridge import import_attestation, wrap_as_event


class TestWrapAsEvent:
    def test_creates_valid_event(self, sample_attestation, oracle_key):
        imported = import_attestation(sample_attestation, oracle_key)
        event = wrap_as_event(imported, oracle_key)
        assert event.verify()

    def test_event_kind_1990(self, sample_attestation, oracle_key):
        imported = import_attestation(sample_attestation, oracle_key)
        event = wrap_as_event(imported, oracle_key)
        assert event.kind == 1990

    def test_event_pubkey_matches(self, sample_attestation, oracle_key):
        imported = import_attestation(sample_attestation, oracle_key)
        event = wrap_as_event(imported, oracle_key)
        assert event.pubkey == oracle_key.xonly_pubkey_hex

    def test_event_has_d_tag(self, sample_attestation, oracle_key):
        imported = import_attestation(sample_attestation, oracle_key)
        event = wrap_as_event(imported, oracle_key)
        d_tags = [t for t in event.tags if t[0] == "d"]
        assert len(d_tags) == 1

    def test_event_has_t_tag_infer(self, sample_attestation, oracle_key):
        imported = import_attestation(sample_attestation, oracle_key)
        event = wrap_as_event(imported, oracle_key)
        t_tags = [t for t in event.tags if t[0] == "t"]
        assert len(t_tags) == 1
        assert t_tags[0][1] == "infer"

    def test_event_content_is_base64(self, sample_attestation, oracle_key):
        import base64
        imported = import_attestation(sample_attestation, oracle_key)
        event = wrap_as_event(imported, oracle_key)
        decoded = base64.b64decode(event.content)
        assert b'"action_type"' in decoded or b'"infer"' in decoded

    def test_event_timestamp_matches_action(self, sample_attestation, oracle_key):
        imported = import_attestation(sample_attestation, oracle_key)
        event = wrap_as_event(imported, oracle_key)
        assert event.created_at == imported.signed_action.action.ts

    def test_roundtrip_decode(self, sample_attestation, oracle_key):
        from vrt1_agents.nostr import decode_action_event

        imported = import_attestation(sample_attestation, oracle_key)
        event = wrap_as_event(imported, oracle_key)
        recovered = decode_action_event(event)
        assert recovered.id == imported.signed_action.id
        assert recovered.action.action_type == "infer"
        assert recovered.verify()
