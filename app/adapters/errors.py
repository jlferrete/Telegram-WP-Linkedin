from __future__ import annotations


class AdapterError(Exception):
    """Base exception for adapter failures."""


class AdapterContractError(AdapterError):
    """Raised when a provider response does not match expected contract."""
