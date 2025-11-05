from typing import Dict, Any
import io
import os

from openai import OpenAI


def get_openai_client() -> OpenAI:
	api_key = os.getenv("OPENAI_API_KEY")
	if not api_key:
		raise RuntimeError("OPENAI_API_KEY environment variable is not set.")
	return OpenAI(api_key=api_key)


def transcribe_audio_bytes(audio_bytes: bytes, filename: str = "audio.wav") -> str:

	client = get_openai_client()
	file_like = io.BytesIO(audio_bytes)
	file_like.name = filename
	transcription = client.audio.transcriptions.create(
		model="gpt-4o-mini-transcribe", 
		file=file_like
	)
	return transcription.text


def chat_with_json_response(
	user_text: str,
	system_prompt: str,
	model: str = "gpt-4o-mini",
) -> Dict[str, Any]:

	client = get_openai_client()

	completion = client.chat.completions.create(
		model=model,
		messages=[
			{"role": "system", "content": system_prompt},
			{"role": "user", "content": user_text},
		],
	)
	message = completion.choices[0].message
	if not message.content:
		raise RuntimeError("Empty response from model.")

	import json
	try:
		return json.loads(message.content)
	except Exception:
		# Fallback: model returned plain text instead of JSON; wrap it so the app can proceed.
		raw_text = message.content.strip()
		return {
			"type": "pdf",
			"title": "Synthèse entretien",
			"content": raw_text,
		}


