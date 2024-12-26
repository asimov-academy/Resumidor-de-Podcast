from pytubefix import YouTube
import ffmpeg
import re

# Extração de áudio
base_dir = f"audios"
video_url = "https://www.youtube.com/watch?v=JlnchqiINg8&t=10952s"
print(f"Downloading {video_url}.")

yt = YouTube(video_url)
stream_url = yt.streams[0].url
sanitized_title = re.sub(r'[\\/*?:"<>|]', "", yt.title)
audio_path = f"{base_dir}/{sanitized_title}.mp3"

audio, err = (
    ffmpeg
    .input(stream_url)
    .output("pipe:", format='mp3',  
            acodec='libmp3lame', 
            ar='22050',  
            ac=1, 
            loglevel="error")  
    .run(capture_stdout=True)
)


with open(audio_path, 'wb') as f:
    f.write(audio)
