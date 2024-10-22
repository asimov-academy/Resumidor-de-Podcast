import whisperx
from dotenv import load_dotenv, find_dotenv
import os
_ = load_dotenv(find_dotenv())

device = "cuda" 
audio_file = "audios/Como fazer um lançamento digital passo a passo (com Fernando Miranda) | ROI Hunters #263.mp3"
batch_size = 16
compute_type = "float16"

model = whisperx.load_model("large-v2", 
                            device, 
                            compute_type=compute_type)

audio = whisperx.load_audio(audio_file)
result = model.transcribe(audio, batch_size=batch_size)


diarize_model = whisperx.DiarizationPipeline(use_auth_token=os.environ["HF_API_KEY"], 
                                             device=device)

diarize_segments = diarize_model(audio)
# diarize_model(audio, min_speakers=min_speakers, max_speakers=max_speakers)

result = whisperx.assign_word_speakers(diarize_segments, result)
print(diarize_segments)
print(result["segments"]) # segments are now assigned speaker IDs

final_transcript = ""
for segment in result["segments"]:
    final_transcript += f"{segment['speaker']}:\n"
    final_transcript += segment["text"]
    final_transcript += "\n\n"

open("transcript.txt", "wb").write(final_transcript.encode('utf-8'))