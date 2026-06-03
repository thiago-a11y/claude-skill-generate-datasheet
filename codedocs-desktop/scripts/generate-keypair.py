#!/usr/bin/env python3
"""Generate Ed25519 keypair for CodeDocs Desktop licensing.

Run ONCE. Save the private key securely (never commit it).
The public key goes embedded in the app.

Usage:
    python3 scripts/generate-keypair.py
"""

import base64
import os
from nacl.signing import SigningKey

key = SigningKey.generate()
private_b64 = base64.b64encode(bytes(key)).decode()
public_b64 = base64.b64encode(bytes(key.verify_key)).decode()

print("=" * 60)
print("CodeDocs Desktop — Ed25519 Keypair")
print("=" * 60)
print()
print(f"PRIVATE KEY (keep secret, never commit):")
print(f"  {private_b64}")
print()
print(f"PUBLIC KEY (embed in the app):")
print(f"  {public_b64}")
print()

# Save to .env (gitignored)
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
with open(env_path, "w") as f:
    f.write(f"CODEDOCS_LICENSE_PRIVATE_KEY={private_b64}\n")
    f.write(f"CODEDOCS_LICENSE_PUBLIC_KEY={public_b64}\n")

print(f"Saved to {os.path.abspath(env_path)}")
print("Add .env to .gitignore (should already be there).")
