import kallia_core.models as Models
from kallia_core.memories import Memories


def test_histories_to_memories():
    temperature = 0.0
    max_tokens = 8192
    messages = [
        {"role": "user", "content": "What is the weather today in Hong Kong?"},
        {"role": "assistant", "content": "Cloudy, 23°C"},
        {"role": "user", "content": "How about tomorrow?"},
        {"role": "assistant", "content": "Sunny, 31°C"},
    ]
    memories = Memories.create(
        messages=[Models.Message(**history) for history in messages],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    assert memories
