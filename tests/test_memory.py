from src.memory import MemoryStore


def test_memory_store_persists_failures(
    tmp_path,
):

    memory_file = (
        tmp_path / "memory.json"
    )

    memory = MemoryStore(
        path=str(memory_file),
    )

    rejection_log = [
        {
            "attempt": 1,
            "status": "REJECTED",
            "failures": [
                "Incorrect RAG explanation."
            ],
            "recommendations": [
                (
                    "Explain retrieval "
                    "instead of retraining."
                )
            ],
        }
    ]

    memory.save_run(
        topic="Introduction to RAG",
        attempts=2,
        status="PASSED",
        rejection_log=rejection_log,
    )

    failures = memory.get_recent_failures(
        topic="Introduction to RAG",
    )

    assert len(failures) == 1

    assert (
        failures[0]["failures"][0]
        == "Incorrect RAG explanation."
    )