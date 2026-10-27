from gnani.stt import GnaniSTTClient

def transcribe_malayalam(audio_file, api_key: str) -> str:
    """Send a Streamlit audio upload to Gnani and return recognised Malayalam text."""
    client = GnaniSTTClient(api_key=api_key)
    result = client.transcribe(audio_file, language_code="ml-IN")
    if not isinstance(result, dict):
        raise RuntimeError("Gnani returned an unexpected response format.")
    transcript = result.get("transcript", "")
    if transcript is None:
        return ""
    return str(transcript).strip()
