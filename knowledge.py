knowledge = {
    "nexvora": "Nexvora একটি AI studio platform",
    "gpt": "GPT হলো একটি language model",
    "ai": "AI মানে Artificial Intelligence",
    "hello": "হ্যালো! আমি তোমার NexVoice assistant"
}

def get_answer(text):
    text = text.lower()

    # exact match + keyword match
    for key in knowledge:
        if key in text:
            return knowledge[key]

    # fallback logic
    if "তুমি কে" in text:
        return "আমি তোমার personal AI assistant"

    return "দুঃখিত, আমি এই প্রশ্ন বুঝতে পারিনি"
