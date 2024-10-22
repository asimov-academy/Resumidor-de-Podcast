from faster_whisper import WhisperModel
from openai import OpenAI
import ffmpeg
from pytubefix import YouTube
import os
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from groq import Groq
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())


# Extração de áudio
base_dir = f"audios"
video_url = "https://www.youtube.com/watch?v=NjJePURy0MI&t=16s&ab_channel=ROIHunters"
print(f"Downloading {video_url}.")
yt = YouTube(video_url)
stream_url = yt.streams[0].url

audio_path = f"{base_dir}/{yt.title}.mp3"

audio, err = (
    ffmpeg
    .input(stream_url)
    .output("pipe:", format='mp3',  # Formato mp3
            acodec='libmp3lame', 
            ar='22050',  # Taxa de amostragem reduzida
            ac=1,  # Convertendo para mono
            loglevel="error")  
    .run(capture_stdout=True)
)

with open(audio_path, 'wb') as f:
    f.write(audio)



from langchain_community.document_loaders import YoutubeLoader

loader = YoutubeLoader.from_youtube_url(video_url, language=['pt'])
lista_documentos = loader.load()
documento = ''
for doc in lista_documentos:
    documento = documento + doc.page_content


# Groq Transcription
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
with open(audio_path, "rb") as file:
    transcription = client.audio.transcriptions.create(
        file=(os.path.basename(audio_path), file.read()),
        model="whisper-large-v3-turbo",
        response_format="text",
        language="pt",
    )
    print(transcription)



# Podcast Transcript
t1 = time()
whisper_model = WhisperModel("small", 
                                compute_type="int8", 
                                cpu_threads=os.cpu_count(), 
                                num_workers=os.cpu_count())
                                
segments, _ = whisper_model.transcribe(audio_path, 
                                           language="pt")
clean_prompt = "".join(segment.text for 
                           segment in segments).strip()
open("transcript.txt", "w").write(clean_prompt)
print(time() - t1)


t1 = time()
from openai import OpenAI
local_client = OpenAI(api_key="cant-be-empty", 
                        base_url="http://192.168.1.5:8000/v1/")


audio_file = open(audio_path, "rb")
clean_prompt = local_client.audio.transcriptions.create(
    # model="Systran/faster-distil-whisper-large-v3", 
    model="Systran/faster-whisper-small", 
    # model="Systran/faster-whisper-medium", 
    file=audio_file
).text
print(time() - t1)

# Resumi
template="""
    Você é um assistente para resumir Podcasts.

    Você receberá o conteúdo transcrito de um Podcast e deverá
    criar um resumo, contendo: 
    - Introdução
    - Uma descrição do conteúdo transcrito
    - Principais pontos abordados
    - Uma conclusão
    
    Podcast: {input}
    """
prompt_template = PromptTemplate.from_template(template)

chat = ChatOpenAI(model="gpt-4o-mini")
chain = prompt_template | chat