from promptev import PromptevClient
import asyncio

client = PromptevClient(
    project_key="pl_sk_bkcAkOf4pS_zdCrOeSmz8msunT4IOj_6",  # Replace with your real or test key
    base_url="http://localhost:8003",       # Pointing to your local server
)

# Test a prompt without variables
# output = client.get_prompt("test-static-prompt")
# print("Static prompt:", output)

# Test a prompt with variables
output = client.get_prompt("review-user-prompt", {
    "user_prompt_text": "How to improve LLM reasoning?"
})
print("Formatted prompt:", output)

print("-----------------------")
async def main():
    output = await client.aget_prompt("review-user-prompt", {
        "user_prompt_text": "How to improve LLM reasoning?"
    })
    print("a get promt", output)
    return output
print("Formatted async prompt:", asyncio.run(main()))
