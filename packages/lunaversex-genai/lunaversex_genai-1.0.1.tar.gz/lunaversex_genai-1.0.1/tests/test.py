import asyncio
from lunaversex-genai import genai, Message, ChatOptions

async def run_stream():
    messages = [Message(role="user", content="Cuéntame una historia corta")]
    options = ChatOptions(model="lumi-o1-mini")

    async for delta in genai.chatStream(messages, options):
        if delta.type == "delta" and delta.content:
            print(delta.content, end="")
        elif delta.type == "end":
            print("\n[Fin del stream]")

    await genai.close()

asyncio.run(run_stream())
