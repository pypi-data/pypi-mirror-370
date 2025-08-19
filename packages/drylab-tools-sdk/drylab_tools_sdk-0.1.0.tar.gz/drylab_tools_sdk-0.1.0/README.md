DryLab BioAI SDK

Python client SDK for interacting with DryLab BioAI microservices: Boltz, Cellpose, UniMolV2, RFdiffusion, ProteinMPNN, LigandMPNN, AntiFold, DiffDock-PP, ThermoMPNN, ESM3, and ImmuneBuilder.

Installation

```bash
pip install drylab-bioai-sdk
```

Quick start

```python
from drylab import DryLabClient

sdk = DryLabClient()
# Example: ProteinMPNN
files = sdk.proteinmpnn.design(pdb_b64="...", target_dir="/tmp/out", design_chains=["A"])  
print(files)
```

Service URLs

Override service endpoints with environment variables:
- DRYLAB_BOLTZ_URL, DRYLAB_CELLPOSE_URL, DRYLAB_UNIMOLV2_URL, DRYLAB_RFDIFFUSION_URL
- DRYLAB_PROTEINMPNN_URL, DRYLAB_LIGANDMPNN_URL, DRYLAB_ANTIFOLD_URL, DRYLAB_DIFFDOCKPP_URL
- DRYLAB_THERMOMPNN_URL, DRYLAB_ESM3_URL, DRYLAB_IMMUNEBUILDER_URL

Default domains are `[tool].tools.thedrylab.com` and are routed to corresponding FastAPI instances.

License

MIT


