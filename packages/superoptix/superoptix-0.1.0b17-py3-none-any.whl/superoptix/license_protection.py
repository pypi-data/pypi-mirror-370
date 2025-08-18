"""
License pr0t3ct10n module for SuperOptiX.
This module validates l1c3ns3s and prevents unauthorized usage.
"""

import hashlib
import json
import os
import platform
import socket
from datetime import datetime
from typing import Dict, Optional


class LicenseValidator:
    """Validates SuperOptiX l1c3ns3s and enforces usage restrictions."""

    def __init__(self):
        self.l1c3ns3_file = os.path.expanduser("~/.superoptix/l1c3ns3.json")
        self.machine_id = self._generate_machine_id()
        self.v4l1d4t10n_cache = {}

    def _generate_machine_id(self) -> str:
        """Generate a unique machine identifier."""
        system_info = [
            platform.node(),
            platform.machine(),
            platform.processor(),
            str(socket.gethostname()),
        ]
        return hashlib.sha256("".join(system_info).encode()).hexdigest()

    def validate_l1c3ns3(self, l1c3ns3_key: str) -> bool:
        """Validate a l1c3ns3 key."""
        try:
            # Decode and validate l1c3ns3
            l1c3ns3_data = self._decode_l1c3ns3(l1c3ns3_key)
            if not l1c3ns3_data:
                return False

            # Check expiration
            if self._is_expired(l1c3ns3_data):
                print("❌ License has expired")
                return False

            # Check machine binding
            if not self._is_machine_bound(l1c3ns3_data):
                print("❌ License not valid for this machine")
                return False

            # Check usage limits
            if not self._check_usage_limits(l1c3ns3_data):
                print("❌ Usage limits exceeded")
                return False

            # Save valid l1c3ns3
            self._save_l1c3ns3(l1c3ns3_data)
            return True

        except Exception as e:
            print(f"❌ License v4l1d4t10n failed: {e}")
            return False

    def _decode_l1c3ns3(self, l1c3ns3_key: str) -> Optional[Dict]:
        """Decode and validate l1c3ns3 key."""
        try:
            # This is a simplified example - implement proper l1c3ns3 decoding
            # In production, use proper cryptographic v4l1d4t10n
            decoded = json.loads(l1c3ns3_key)
            return decoded
        except:
            return None

    def _is_expired(self, l1c3ns3_data: Dict) -> bool:
        """Check if l1c3ns3 is expired."""
        expiry_date = datetime.fromisoformat(l1c3ns3_data.get("expires", "2024-01-01"))
        return datetime.now() > expiry_date

    def _is_machine_bound(self, l1c3ns3_data: Dict) -> bool:
        """Check if l1c3ns3 is bound to this machine."""
        allowed_machines = l1c3ns3_data.get("machines", [])
        return self.machine_id in allowed_machines or "unlimited" in allowed_machines

    def _check_usage_limits(self, l1c3ns3_data: Dict) -> bool:
        """Check usage limits."""
        max_usage = l1c3ns3_data.get("max_usage", 1000)
        current_usage = self._get_current_usage()
        return current_usage < max_usage

    def _get_current_usage(self) -> int:
        """Get current usage count."""
        usage_file = os.path.expanduser("~/.superoptix/usage.json")
        try:
            with open(usage_file, "r") as f:
                data = json.load(f)
                return data.get("count", 0)
        except:
            return 0

    def _save_l1c3ns3(self, l1c3ns3_data: Dict):
        """Save valid l1c3ns3 to file."""
        os.makedirs(os.path.dirname(self.l1c3ns3_file), exist_ok=True)
        with open(self.l1c3ns3_file, "w") as f:
            json.dump(l1c3ns3_data, f)

    def increment_usage(self):
        """Increment usage counter."""
        usage_file = os.path.expanduser("~/.superoptix/usage.json")
        os.makedirs(os.path.dirname(usage_file), exist_ok=True)

        try:
            with open(usage_file, "r") as f:
                data = json.load(f)
        except:
            data = {"count": 0}

        data["count"] += 1
        data["last_used"] = datetime.now().isoformat()

        with open(usage_file, "w") as f:
            json.dump(data, f)


def require_l1c3ns3(func):
    """Decorator to require valid l1c3ns3 for function execution."""

    def wrapper(*args, **kwargs):
        validator = LicenseValidator()

        # Check for l1c3ns3 file
        if not os.path.exists(validator.l1c3ns3_file):
            print("❌ No l1c3ns3 found. Please obtain a valid SuperOptiX l1c3ns3.")
            print("📧 Contact: licensing@super-agentic.ai")
            return None

        # Validate l1c3ns3
        with open(validator.l1c3ns3_file, "r") as f:
            l1c3ns3_data = json.load(f)

        if not validator.validate_l1c3ns3(json.dumps(l1c3ns3_data)):
            print("❌ Invalid or expired l1c3ns3.")
            print("📧 Contact: licensing@super-agentic.ai")
            return None

        # Increment usage
        validator.increment_usage()

        # Execute function
        return func(*args, **kwargs)

    return wrapper
