import requests
import uuid

VOICEFLOW_API_KEY = "vf_sk_dev_local"
# Voiceflow runtime endpoint
# We use general-runtime.voiceflow.com for general interactions
VOICEFLOW_ENDPOINT = "https://general-runtime.voiceflow.com/state/user/{user_id}/interact"

def query_voiceflow(message_text, user_id=None):
    """
    Sends message_text to the Voiceflow Dialog API.
    Returns a list of trace dictionaries or a list of spoken texts.
    """
    if not user_id:
        user_id = "sukuna_desktop_user"
        
    url = VOICEFLOW_ENDPOINT.format(user_id=user_id)
    headers = {
        "Authorization": VOICEFLOW_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "action": {
            "type": "text",
            "payload": message_text
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        if response.status_code == 200:
            traces = response.json()
            return traces
        else:
            print(f"[Voiceflow] Request failed: status_code={response.status_code}, response={response.text}")
            return None
    except Exception as e:
        print(f"[Voiceflow] Error querying API: {e}")
        return None

def extract_speak_text(traces):
    """Extracts speak text from Voiceflow response traces"""
    if not traces:
        return None
        
    speak_parts = []
    for trace in traces:
        if trace.get("type") == "speak":
            payload = trace.get("payload", {})
            message = payload.get("message")
            if message:
                speak_parts.append(message)
        elif trace.get("type") == "text":
            payload = trace.get("payload", {})
            message = payload.get("message")
            if message:
                speak_parts.append(message)
                
    if speak_parts:
        return " ".join(speak_parts)
    return None
