from recorder import transcribe_audio

# Transcribe the recorded meeting
transcript = transcribe_audio("meeting.wav")

# Show the result
print("📝 Transcription Result:\n")
print(transcript)
