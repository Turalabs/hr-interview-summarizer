# Voice-to-AI Streamlit App

A Streamlit app where you can record or upload audio, transcribe it with Whisper, send the transcript to an OpenAI chat model (guided by a system prompt), and get either a textual answer or a generated PDF to download.

## Features
- Record audio in-browser or upload `.wav/.mp3/.m4a/ogg`
- Transcribe via Whisper (`whisper-1`)
- Ask `gpt-4o-mini` (configurable) with a custom system prompt
- Get back either `text` or `pdf` as a JSON-structured response
- If `pdf`, the app generates a simple PDF for download

## Setup
1. Ensure Python 3.9+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your OpenAI API key (Windows PowerShell example):
   ```powershell
   setx OPENAI_API_KEY "YOUR_KEY_HERE"
   # Restart PowerShell or your machine for setx to take effect
   ```
   Or create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=YOUR_KEY_HERE
   ```

## Run
```bash
streamlit run app/streamlit_app.py
```

## How it works
- The app captures audio (record or upload) and sends it to Whisper for transcription.
- The transcript is submitted to the selected chat model with your system prompt.
- The model returns a JSON object, for example:
  ```json
  {"type":"pdf","title":"Weekly Summary","content":"..."}
  ```
- If `type` is `pdf`, the app generates a PDF and offers a download button; otherwise it displays the text.

## Notes
- Microphone recording uses `audio-recorder-streamlit`. If recording isn’t supported in your browser/OS, upload a file instead.
- For best results, keep audio under a couple of minutes.

