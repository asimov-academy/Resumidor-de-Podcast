import whisperx
import os
from time import time

t1 = time()
audio_file = "audios/Como fazer um lançamento digital passo a passo (com Fernando Miranda) | ROI Hunters #263.mp3"

model = whisperx.load_model("small", 
                            device="cuda",
                            compute_type="int8")
audio = whisperx.load_audio(audio_file)
result = model.transcribe(audio)
print("Total time elapsed: ", time() - t1)
print("Transcription: ", result["segments"])



diarize_model = whisperx.DiarizationPipeline(
    use_auth_token=os.environ["HF_API_KEY"])

diarize_segments = diarize_model(audio)

result = whisperx.assign_word_speakers(diarize_segments, result)
print(diarize_segments)
print(result["segments"])

final_transcript = ""
for segment in result["segments"]:
    final_transcript += f"{segment['speaker']}:\n"
    final_transcript += segment["text"]
    final_transcript += "\n\n"



# ===============
# Podcast Resumer
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())


template="""
    Você é um assistente para resumir Podcasts.

    Você receberá o conteúdo transcrito de um Podcast e deverá
    criar um resumo, em MARKDOWN, contendo: 
    1. Uma introdução
        - Escreva 1 parágrafo com uma introdução sobre o que foi falado no podcast
    
    2. Os principais pontos abordados, em ordem cronológica. Numere-os.
        - Escreva um texto bem completo sobre cada um dos pontos. Seja específico.
    
    3. Uma conclusão
        - Escreva um parágrafo sobre conclusão.
    
    Podcast: {input}
    """
prompt_template = PromptTemplate.from_template(template)

chat = ChatOpenAI(model="gpt-4o-mini")
chain = prompt_template | chat

transcript = open("transcript.txt", "r").read()
response = chain.invoke({"input": final_transcript})

open("summary.md", "w").write(response.content)
