from config import model

def generate_new_message(transcription):
    return [
        {
            "role": "user",
            "content": {
                "parts": [
                    {
                        "text": f"Always respond in the language the user speaks to you in. Do not respond with symbols or strange characters. Do not use asterisks. User: {transcription}"
                    }
                ]
            }
        }
    ]

def process_transcription(transcription, script):
    try:
        messages = script + generate_new_message(transcription)
        content_messages = [
            {
                "role": message["role"],
                "parts": [{"text": part["text"]} for part in message["content"]["parts"]]
            }
            for message in messages
        ]
        response = model.generate_content(content_messages)
        return response.text
    except Exception as e:
        print(f"Error in process_transcription: {e}")
        return ""