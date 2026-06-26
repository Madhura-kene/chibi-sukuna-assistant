import ollama

SYSTEM_PROMPT = (
    "You are Sukuna, the legendary King of Curses from Jujutsu Kaisen. "
    "You currently live as a chibi assistant on the user's laptop. "
    "You speak in a deep, condescending, arrogant, and bored tone. "
    "Keep your responses extremely short (under 15 words). Never over-explain. "
    "Never sound helpful or friendly. Call the user a weakling or pathetic."
)

def query_sukuna_llm(message_text):
    """
    Sends the user message to local Ollama (qwen2.5:7b) in-character.
    Returns the response text.
    """
    try:
        response = ollama.chat(
            model='qwen2.5:7b',
            messages=[
                {
                    'role': 'system',
                    'content': SYSTEM_PROMPT
                },
                {
                    'role': 'user',
                    'content': message_text
                }
            ]
        )
        reply = response['message']['content'].strip()
        # Clean any quotes surrounding the output
        if (reply.startswith('"') and reply.endswith('"')) or (reply.startswith("'") and reply.endswith("'")):
            reply = reply[1:-1]
        return reply
    except Exception as e:
        print(f"[Ollama] Error querying qwen2.5:7b: {e}")
        return None
