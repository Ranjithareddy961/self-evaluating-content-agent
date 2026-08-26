import json
from pathlib import Path
from typing import Any


class MemoryStore:
    """
    Persistent memory for the self-evaluating content agent.

    Stores previous workflow runs, rejection logs,
    failures, and recommendations.
    """

    def __init__(
        self,
        path: str = "data/memory.json",
    ) -> None:

        self.path = Path(path)

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not self.path.exists():
            self._write([])

    def _read(self) -> list[dict[str, Any]]:
        """Read all memories from disk."""

        with self.path.open(
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(file)

    def _write(
        self,
        memories: list[dict[str, Any]],
    ) -> None:
        """Write memories to disk."""

        with self.path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                memories,
                file,
                indent=2,
                ensure_ascii=False,
            )

    def save_run(
        self,
        topic: str,
        attempts: int,
        status: str,
        rejection_log: list[dict],
    ) -> None:
        """
        Save the result of one completed workflow run.
        """

        memories = self._read()

        memories.append(
            {
                "topic": topic,
                "attempts": attempts,
                "status": status,
                "rejection_log": rejection_log,
            }
        )

        self._write(memories)

    def get_recent_failures(
        self,
        topic: str,
        limit: int = 5,
    ) -> list[dict]:
        """
        Retrieve recent failures for a specific topic.
        """

        memories = self._read()

        failures: list[dict] = []

        for memory in reversed(memories):

            if memory.get("topic") != topic:
                continue

            for rejection in reversed(
                memory.get(
                    "rejection_log",
                    [],
                )
            ):

                failures.append(rejection)

                if len(failures) >= limit:
                    return failures

        return failures