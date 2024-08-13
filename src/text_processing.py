from config import model

def generate_new_message(transcription):
    return [
        {
            "role": "user",
            "content": {
                "parts": [
                    {
                        "text": f"Responde siempre en el lenguaje que te habla el usuario. No respondas con simbolos ni caracteres extraños. No uses asteriscos. User: {transcription}"
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
        print(f"Error en process_transcription: {e}")
        return ""