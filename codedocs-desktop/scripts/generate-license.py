#!/usr/bin/env python3
"""Generate a signed Pro license key for CodeDocs Desktop.

Usage:
    python3 scripts/generate-license.py --customer "Empresa X" --days 365
    python3 scripts/generate-license.py --customer "Thiago" --days 30

Reads CODEDOCS_LICENSE_PRIVATE_KEY from .env file.
Outputs a license key that the user pastes into the app.
"""

import argparse
import base64
import json
import os
import sys
from datetime import datetime, timedelta

try:
    from nacl.signing import SigningKey
except ImportError:
    print("ERROR: pip install pynacl")
    sys.exit(1)


def load_private_key() -> SigningKey:
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if not os.path.exists(env_path):
        print("ERROR: .env not found. Run generate-keypair.py first.")
        sys.exit(1)

    with open(env_path) as f:
        for line in f:
            if line.startswith("CODEDOCS_LICENSE_PRIVATE_KEY="):
                key_b64 = line.strip().split("=", 1)[1]
                return SigningKey(base64.b64decode(key_b64))

    print("ERROR: CODEDOCS_LICENSE_PRIVATE_KEY not found in .env")
    sys.exit(1)


def generate_license(customer_id: str, days: int, edition: str = "pro") -> str:
    key = load_private_key()

    payload = {
        "app_id": "codedocs-desktop",
        "edition": edition,
        "modules": ["technical-spec", "migration-plan", "sales-datasheet", "targets"],
        "customer_id": customer_id,
        "issued_at": datetime.utcnow().isoformat() + "Z",
        "expires_at": (datetime.utcnow() + timedelta(days=days)).isoformat() + "Z",
    }

    header_b64 = base64.urlsafe_b64encode(
        json.dumps({"typ": "JWT", "alg": "Ed25519"}).encode()
    ).rstrip(b"=").decode()

    payload_b64 = base64.urlsafe_b64encode(
        json.dumps(payload).encode()
    ).rstrip(b"=").decode()

    message = f"{header_b64}.{payload_b64}".encode()
    signed = key.sign(message)
    signature_b64 = base64.urlsafe_b64encode(signed.signature).rstrip(b"=").decode()

    token = f"{header_b64}.{payload_b64}.{signature_b64}"
    return token, payload


def main():
    parser = argparse.ArgumentParser(description="Generate CodeDocs Desktop Pro license")
    parser.add_argument("--customer", required=True, help="Customer name or ID")
    parser.add_argument("--days", type=int, default=365, help="License duration in days (default: 365)")
    parser.add_argument("--edition", default="pro", help="Edition (default: pro)")
    args = parser.parse_args()

    token, payload = generate_license(args.customer, args.days, args.edition)

    print()
    print("=" * 60)
    print("CodeDocs Desktop — Licença Pro")
    print("=" * 60)
    print(f"  Cliente:    {args.customer}")
    print(f"  Edição:     {args.edition}")
    print(f"  Validade:   {args.days} dias")
    print(f"  Expira em:  {payload['expires_at'][:10]}")
    print(f"  Módulos:    {', '.join(payload['modules'])}")
    print()
    print("CHAVE DE LICENÇA (cole no app):")
    print()
    print(token)
    print()
    print(f"Tamanho: {len(token)} caracteres")
    print("=" * 60)


if __name__ == "__main__":
    main()
