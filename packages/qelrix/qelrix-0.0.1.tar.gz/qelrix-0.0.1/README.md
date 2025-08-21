# Qelrix

Qelrix is a simple Python library for interacting with the Gemini API.

## Installation

```bash
pip install qelrix
```

## Usage

```python
import qelrix

qelrix.apikey("YOUR_API_KEY")
qelrix.model("YOUR_GEMINI_ENDPOINT")
qelrix.hoi("Hello, how are you?")
print(qelrix.traloi())
```

## API

### `qelrix.apikey(key: str) -> str`
Sets the API key.

### `qelrix.model(url: str) -> str`
Sets the full Gemini API endpoint URL.

### `qelrix.hoi(text: str)`
Sends a question to the API and stores the response.

### `qelrix.traloi() -> str`
Retrieves the answer from the last `hoi()` call.


