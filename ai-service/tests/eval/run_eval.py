import json
import os
import pytest
from app.intent import extract_intent
from app.config import settings

@pytest.mark.asyncio
async def test_run_eval_dataset():
    eval_file = os.path.join(os.path.dirname(__file__), "intent_cases.jsonl")
    assert os.path.exists(eval_file), f"Eval dataset not found at {eval_file}"

    cases = []
    with open(eval_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                cases.append(json.loads(line))

    assert len(cases) >= 50, f"Expected 50+ cases, found {len(cases)}"

    correct_intents = 0
    total = len(cases)

    for case in cases:
        inp = case["input"]
        expected = case["expected"]

        # Call extraction (uses Ollama if available, otherwise heuristic fallback)
        res = await extract_intent(
            message=inp,
            collected_fields={},
            ollama_url=settings.OLLAMA_URL,
            model=settings.OLLAMA_MODEL,
            timeout=2.0,  # Fast timeout for CI / unit test
        )

        if res.intent == expected["intent"]:
            correct_intents += 1

    accuracy = correct_intents / total
    print(f"\n[Intent Eval] Evaluated {total} prompts. Intent accuracy: {accuracy:.2%}")
    # Heuristic + model baseline check
    assert accuracy >= 0.70, f"Accuracy {accuracy:.2%} is below benchmark requirement"
