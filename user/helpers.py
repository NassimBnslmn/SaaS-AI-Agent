import requests

def send_to_n8n(user_id, email, google_access_token, google_refresh_token=None):
    print(f"Sending data to n8n for user {user_id} with email {email}")
    url = "https://n8n.ter-ia.studio/webhook/create-client-sheets"

    payload = {
        "userId": user_id,
        "email": email,
        "googleAccessToken": google_access_token,
    }

    if google_refresh_token:
        payload["googleRefreshToken"] = google_refresh_token

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending request to n8n: {e}")
        return None
