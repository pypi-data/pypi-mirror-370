# vibedecrement

AI-powered number decrementing using GPT.

## Usage

Install the package:
```bash
pip install vibedecrement
```

Set your OpenAI API key as an environment variable.
```bash
export OPENAI_API_KEY=your_key_here
```

```python
from vibedecrement import vibedecrement

result = vibedecrement(5)
print(result)  # 4

result = vibedecrement(42)
print(result)  # 41

# Edge case - decrementing 1 returns 0
result = vibedecrement(1)
print(result)  # 0
```

## Test

```bash
pytest tests/
```

## Dependencies

- openai
- pydantic
- typing-extensions

⚠️ Requires OpenAI API key. Only accepts positive numbers (> 0). Experimental project - not for production use.