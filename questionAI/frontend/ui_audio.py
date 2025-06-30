# import streamlit as st
# from streamlit_audio_recorder import audio_recorder

# st.title("🎤 Speak Your Question")

# # Record audio from microphone
# audio_bytes = audio_recorder(
#     text="Click to record your question",
#     icon_size="2x",
#     recording_color="#e83e8c",  # Optional: make it prettier
#     neutral_color="#6c757d"
# )

# # Playback
# if audio_bytes:
#     st.audio(audio_bytes, format="audio/wav")
#     st.success("Audio recorded successfully!")

#     # Optionally save or send it to an API
#     with open("question.wav", "wb") as f:
#         f.write(audio_bytes)
#     st.info("Saved as 'question.wav'")