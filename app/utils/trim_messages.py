from langchain_core.messages.utils import count_tokens_approximately

def count_tokens(messages):
        total_tokens = 0
        for msg in messages:
            total_tokens += count_tokens_approximately(msg['content'])
        return total_tokens

def trim_message_history(messages):
        total_tokens = count_tokens(messages)

        while total_tokens > 32000 and len(messages) > 0:
            removed_message = messages.pop(0)
            total_tokens -= count_tokens_approximately(removed_message['content'])

        return messages


