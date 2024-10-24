from pytubefix import YouTube
import ffmpeg


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
    .output("pipe:", format='mp3',  
            acodec='libmp3lame', 
            ar='22050',  
            ac=1, 
            loglevel="error")  
    .run(capture_stdout=True)
)

with open(audio_path, 'wb') as f:
    f.write(audio)
