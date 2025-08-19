#!/usr/bin/env python3
"""
Validate database hash against expected hash
"""

import argparse
import hashlib
import os
import sys


def calculate_db_hash(db_path: str) -> str:
    """Calculate SHA256 hash of the database file"""
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found: {db_path}")

    hash_sha256 = hashlib.sha256()
    with open(db_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)

    return hash_sha256.hexdigest()


def main():
    parser = argparse.ArgumentParser(description="Validate database hash")
    parser.add_argument("--db", required=True, help="Path to the database file")
    parser.add_argument("--expected-hash", required=True, help="Expected hash value")

    args = parser.parse_args()

    try:
        actual_hash = calculate_db_hash(args.db)
        expected_hash = args.expected_hash.strip()

        if actual_hash == expected_hash:
            print("[SUCCESS] Database hash validation: SUCCESS")
            print(f"   Expected: {expected_hash}")
            print(f"   Actual:   {actual_hash}")
            return 0
        else:
            print("[FAILURE] Database hash validation: FAILURE")
            print(f"   Expected: {expected_hash}")
            print(f"   Actual:   {actual_hash}")
            return 1

    except Exception as e:
        print(f"[ERROR] Error validating database hash: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
