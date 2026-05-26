# vrt1-agent-bridge

Bridge [VERITAS](https://github.com/Ifasola34/veritas) inference attestations into [vrt1-agents](https://github.com/Ifasola34/vrt1-agents) action format.

## What it does

Converts a VERITAS `SignedAttestation` (an oracle certifying an AI inference result) into a vrt1-agents `SignedAction` with `action_type="infer"`. This lets inference results enter the agent reputation graph — other agents can vouch for or dispute inference quality.

The bridge preserves cryptographic continuity: the same BIP-340 key signs both the original attestation and the agent action, and the attestation signature is embedded in action params for full traceability.

## Usage

```python
from veritas.attestation import SignedAttestation
from veritas.crypto import OracleKey
from vrt1_agent_bridge import import_attestation, wrap_as_event

key = OracleKey.from_hex("...")
signed_att = SignedAttestation.from_json(raw)

# Convert to agent action
imported = import_attestation(signed_att, key)
print(imported.signed_action.action.action_type)  # "infer"
print(imported.signed_action.verify())             # True

# Publish as Nostr kind-1990 event
event = wrap_as_event(imported, key)
print(event.kind)    # 1990
print(event.verify())  # True
```

### Verify the full chain

```python
from vrt1_agent_bridge.verify import verify_bridge_chain

assert verify_bridge_chain(imported.signed_action, signed_att)
```

### Batch import

```python
from vrt1_agent_bridge import import_batch

results = import_batch(attestation_list, key)
```

## Field Mapping

| VERITAS Attestation | Agent Action |
|---------------------|--------------|
| `oracle` | `agent` |
| `model` | `target` |
| `input_hash` | `params.input_hash` |
| `epoch` | `params.epoch` |
| `sig` | `params.attestation_sig` |
| `output` (dict) | `outcome` (direct) |
| `output` (non-dict) | `outcome.output` |
| `ts` | `ts` |

## Install

```
pip install git+https://github.com/Ifasola34/vrt1-agent-bridge.git
```

## License

MIT
