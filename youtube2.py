import os
import tempfile
from pytube import YouTube
from moviepy.editor import AudioFileClip
import openai
import streamlit as st

def download_youtube_video(url):
    try:
        yt = YouTube(url)
        video = yt.streams.first()
        return video.download()
    except Exception as e:
        raise Exception("Failed to download YouTube video") from e

def extract_and_chunk_audio(video_path):
    try:
        audio_clip = AudioFileClip(video_path)
        duration = audio_clip.duration
        audio_chunks = []

        for i in range(0, int(duration), 30):
            end = i + 30 if i + 30 < duration else duration
            chunk_path = f"{tempfile.gettempdir()}/{i}_{end}.wav"
            audio_chunk = audio_clip.subclip(i, end)
            audio_chunk.write_audiofile(chunk_path)
            audio_chunks.append(chunk_path)
        
        return audio_chunks
    except Exception as e:
        raise Exception("Failed to extract and chunk audio") from e

def transcribe_audio_chunks(audio_chunks):
    try:
        transcriptions = []

        for chunk in audio_chunks:
            with open(chunk, "rb") as audio_file:
                response = openai.Audio.transcribe(model="whisper-1", file=audio_file, response_format="json")
                transcriptions.append(response['text'])
        
        return ' '.join(transcriptions)
    except openai.errors.OpenAIError as e:
        raise Exception("Failed to transcribe audio") from e

def cleanup_files(video_path, audio_chunks):
    try:
        os.remove(video_path)
        for chunk in audio_chunks:
            os.remove(chunk)
    except Exception as e:
        raise Exception("Failed to clean up temporary files") from e

def main():
    st.title('YouTube Video Transcriber')
    url = st.text_input('Enter a YouTube Video URL', '')
    
    if st.button('Transcribe'):
        try:
            video_path = download_youtube_video(url)
            audio_chunks = extract_and_chunk_audio(video_path)
            transcription = transcribe_audio_chunks(audio_chunks)

            with open('transcription.txt', 'w') as f:
                f.write(transcription)

            st.write(transcription)

            cleanup_files(video_path, audio_chunks)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
