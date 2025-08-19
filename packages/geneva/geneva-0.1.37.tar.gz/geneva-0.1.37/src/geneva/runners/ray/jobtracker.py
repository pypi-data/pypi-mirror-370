# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import attrs
import ray


@ray.remote
@attrs.define
class JobTracker:
    """
    Centralized progress ledger for a job.
    - Metrics are arbitrary strings -> {n, total, done, desc}
    - All ops are atomic via the actor's mailbox.
    """

    job_id: str
    metrics: dict[str, dict] = attrs.field(factory=dict)

    def _upsert(
        self, name: str, *, total: int | None = None, desc: str | None = None
    ) -> None:
        """
        Given a metric 'name', ensure that the metric entry is present with specified
        values or initialized with 0s
        """
        m = self.metrics.get(name)
        if m is None:
            m = {"n": 0, "total": 0, "done": False, "desc": name}
            self.metrics[name] = m
        if total is not None:
            m["total"] = int(total)
        if desc is not None:
            m["desc"] = desc
        # auto-done if we’re already at/over total
        if m["total"] and m["n"] >= m["total"]:
            m["done"] = True

    # Generic metric API
    def set_total(self, name: str, total: int) -> None:
        self._upsert(name, total=total)

    def set_desc(self, name: str, desc: str) -> None:
        self._upsert(name, desc=desc)

    def set(self, name: str, n: int) -> None:
        self._upsert(name)
        m = self.metrics[name]
        m["n"] = int(n)
        if m["total"] and m["n"] >= m["total"]:
            m["done"] = True

    def increment(self, name: str, delta: int = 1) -> None:
        self._upsert(name)
        m = self.metrics[name]
        m["n"] += int(delta)
        if m["total"] and m["n"] >= m["total"]:
            m["done"] = True

    def mark_done(self, name: str) -> None:
        self._upsert(name)
        self.metrics[name]["done"] = True

    # Read APIs
    def get_progress(self, name: str) -> dict:
        self._upsert(name)
        m = self.metrics[name]
        return {"n": m["n"], "total": m["total"], "done": m["done"], "desc": m["desc"]}

    def get_all(self) -> dict[str, dict]:
        # Shallow copy for safety
        return {k: dict(v) for k, v in self.metrics.items()}
