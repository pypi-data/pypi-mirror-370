# -*- coding: utf-8 -*-
# pylint: disable=invalid-name

"""\
Job status utilities
----------------------
"""

import enum


class JobStatus(enum.IntFlag):
    """Flags indicating job status"""

    invalid = 0
    deleted = enum.auto()
    failed = enum.auto()
    submitted = enum.auto()
    running = enum.auto()
    completed = enum.auto()
    converged = enum.auto()
    succeeded = enum.auto()

    def to_json(self):
        """Convert to JSON for serialization"""
        return f"{self.value}"
