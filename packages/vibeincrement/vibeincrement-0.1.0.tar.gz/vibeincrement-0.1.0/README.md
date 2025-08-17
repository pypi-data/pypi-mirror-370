# vibeincrement

AI-powered number incrementing using GPT.

## Usage

Install the package:
```bash
pip install vibeincrement
```

Set your OpenAI API key as an environment variable.
```bash
export OPENAI_API_KEY=your_key_here
```

```python
from vibeincrement import vibeincrement

result = vibeincrement(5)
print(result)  # 6

result = vibeincrement(42)
print(result)  # 43
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