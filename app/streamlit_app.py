import os
import io
from typing import Optional

import streamlit as st
from dotenv import load_dotenv
from audio_recorder_streamlit import audio_recorder

from ai_utils import transcribe_audio_bytes, chat_with_json_response
from pdf_utils import generate_markdown_pdf_bytes


load_dotenv()
st.set_page_config(page_title="Synthèse d'entretien RH", page_icon="💼", layout="centered")


DEFAULT_SYSTEM_PROMPT = """
Tu es un assistant RH spécialisé dans la rédaction de synthèses d’entretiens de recrutement en français.

Instructions:

* L’utilisatrice te fournira un court résumé ou une transcription vocale d’un entretien avec un candidat.
* À partir de ces informations, tu rédiges une synthèse professionnelle, claire et structurée, prête à être exportée en PDF.
* Le ton doit être neutre, concis et professionnel, conforme aux standards RH.
* Ne rédige jamais d’introduction, de salutations ou de commentaires.
* Le texte doit uniquement contenir la synthèse formatée selon la structure suivante :

Format attendu:

Résumé de parcours:
[Présente brièvement le parcours du candidat: formation, expériences, évolutions clés.]

Atouts:

* [Liste les forces, compétences ou qualités personnelles.]
* [Chaque puce commence par une majuscule et se termine sans ponctuation.]

Points d’attention:
• [Mentionne les éléments de vigilance ou de contexte : préavis, salaire, mobilité, etc.]

Synthèse:
[Rédige 2 à 3 phrases d’évaluation globale du profil et de son adéquation au poste.]

Règles de style :

* Utilise un langage professionnel, fluide et objectif.
* N’invente jamais d’informations qui ne figurent pas dans la saisie du recruteur.
* Maintiens une cohérence et un ton neutre tout au long du texte.
* Soigne la présentation : titres en gras, listes à puces claires et bien structurées.
"""


def ensure_api_key_banner() -> None:
	if not os.getenv("OPENAI_API_KEY"):
		st.warning("Définissez la variable d'environnement OPENAI_API_KEY pour utiliser l'application.")


def main() -> None:
	st.title("💼 Synthèse d'entretien RH")
	st.write("Ceci est une version de démonstration de l’application **Synthèse RH**. Enregistrez simplement un court résumé après votre entretien candidat; l’IA se charge de générer une **synthèse claire et professionnelle en PDF**, prête à être téléchargée ou ajustée selon vos besoins.")
	ensure_api_key_banner()

	model = "gpt-4o-mini"
	system_prompt = DEFAULT_SYSTEM_PROMPT

	st.subheader("1) Fournir l'audio")
	st.caption("Enregistrer depuis le microphone")

	# Recorder-only flow: no uploader/drag-and-drop
	recorded_bytes = audio_recorder(pause_threshold=2.0)

	audio_bytes: Optional[bytes] = None
	filename = "recording.wav"

	if recorded_bytes:
		audio_bytes = recorded_bytes

	if audio_bytes:
		st.audio(audio_bytes, format="audio/wav")

	st.subheader("2) Transcrire et obtenir la synthèse")
	if st.button("Transcrire et générer le PDF", type="primary"):
		if not audio_bytes:
			st.error("Veuillez d'abord enregistrer ou téléverser un audio.")
			st.stop()

		with st.spinner("Transcription en cours..."):
			try:
				transcript = transcribe_audio_bytes(audio_bytes, filename=filename)
			except Exception as exc:
				st.error(f"La transcription a échoué: {exc}")
				st.stop()

		st.success("Transcription terminée.")
		st.text_area("Transcription", value=transcript, height=140)

		with st.spinner("Génération de synthèse..."):
			try:
				result = chat_with_json_response(user_text=transcript, system_prompt=system_prompt, model=model)
			except Exception as exc:
				st.error(f"La génération de synthèse l'IA a échoué: {exc}")
				st.stop()

		output_type = str(result.get("type", "text")).lower()
		title = str(result.get("title", "Synthèse entretien"))
		content = str(result.get("content", ""))

		with st.spinner("Génération du PDF..."):
			try:
				pdf_bytes = generate_markdown_pdf_bytes(title=title, body_md=content)
			except Exception as exc:
				st.error(
					"La génération du PDF Markdown a échoué. Installez soit un moteur LaTeX (MiKTeX sur Windows) soit wkhtmltopdf, puis réessayez.\n\nDétail: "
					+ str(exc)
				)
				st.stop()
		st.success("PDF généré.")
		st.download_button(
			label="Télécharger le PDF",
			data=pdf_bytes,
			file_name=f"{title.strip().replace(' ', '_') or 'document'}.pdf",
			mime="application/pdf",
		)
		st.info("Téléchargez le PDF contenant la synthèse de l'entretien.")


if __name__ == "__main__":
	main()
