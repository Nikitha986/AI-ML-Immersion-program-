"""Simple payments stub for marking paid applications (test mode).

This is an in-memory stub intended for demo and unit testing. It lets
the rest of the system mark a (candidate_id, job_id) pair as paid and
query whether it is paid. Persisting to disk or integrating a real
gateway is out of scope for this task.
"""
from typing import Tuple


class PaymentsStub:
    def __init__(self):
        # store paid keys as set of (candidate_id, job_id)
        self._paid = set()

    def mark_paid(self, candidate_id: str, job_id: str) -> None:
        self._paid.add((candidate_id, job_id))

    def is_paid(self, candidate_id: str, job_id: str) -> bool:
        return (candidate_id, job_id) in self._paid


# module-level singleton for simple demos
_GLOBAL = PaymentsStub()


def mark_paid(candidate_id: str, job_id: str) -> None:
    _GLOBAL.mark_paid(candidate_id, job_id)


def is_paid(candidate_id: str, job_id: str) -> bool:
    return _GLOBAL.is_paid(candidate_id, job_id)


def reset():
    _GLOBAL._paid.clear()
