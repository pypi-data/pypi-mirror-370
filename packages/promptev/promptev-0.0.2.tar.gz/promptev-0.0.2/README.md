# promptev-client

A lightweight Python SDK to securely fetch compiled prompts from [Promptev.ai](https://promptev.ai) using your project API key.

---

## Installation

```bash
pip install promptev
```

---

## What is Promptev?

[Promptev](https://promptev.ai) helps teams manage, version, and collaborate on AI prompts at scale, with variables, live context packs, histories, cost estimation, and SDK access.

---

## Usage

### 1. Initialize the client

```python
from promptev import PromptevClient

client = PromptevClient(project_key="pv_sk_abc123yourkey")
```

---

### 2. Fetch a prompt with variables

```python
output = client.get_prompt("onboarding-email", {
    "name": "Ava",
    "product": "Promptev"
})

print(output)
# Output: "Subject: Welcome, Ava! Hey Ava, Thanks for joining Promptev..."
```

---

### 3. Fetch a prompt without variables

```python
output = client.get_prompt("static-welcome")
print(output)
# Output: "You are a helpful AI assistant ready to support the user."
```

> ⚠️ If the prompt has no variables, you can omit the second argument.

---

### 4. Async Usage (e.g. in FastAPI or notebooks)

```python
import asyncio

async def run():
    prompt = await client.aget_prompt("faq-response", {
        "question": "How do I reset my password?"
    })
    print(prompt)

asyncio.run(run())
```

---

## Example: Use with LLM APIs

### OpenAI

```python
from openai import OpenAI

client = OpenAI(api_key="sk-...")

prompt = promptev_client.get_prompt("explain-topic", {
    "topic": "Prompt Engineering"
})

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}]
)

print(response.choices[0].message.content)
```

---

## Features

- ✅ Supports prompts with or without variables
- 🚀 Server-side compilation via **POST** (no client-side templating)
- ⚡ Sync + Async methods: `get_prompt` and `aget_prompt`
- 🔐 Works with any LLM provider (OpenAI, Claude, Gemini, etc.)

---

## Error Handling

```python
# ❌ Missing required variable
client.get_prompt("onboarding-email", { "name": "Leo" })
# ➜ ValueError: Missing required variables: product
```

---

## Prompt Template Example

```text
Subject: Welcome, {{ name }}!

Hey {{ name }},

Thanks for joining {{ product }}. We're thrilled to have you on board!
```

---

## License

This SDK is **commercial software** by Promptev Inc.

By using this package, you agree to the terms in [`LICENSE.txt`](./LICENSE.txt).

- ✅ Free tier use allowed
- 🚫 Production usage requires a subscription

---

## Contact

- 🌐 https://promptev.ai
- 📧 support@promptev.ai
