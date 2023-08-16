import os
import streamlit as st
from pytube import YouTube
from pytube import exceptions as pytube_exceptions
from moviepy.editor import AudioFileClip
import openai

def get_youtube_url():
    # Get YouTube URL from user
    url = st.text_input("Enter the YouTube URL: ")
    return url

def download_video(url):
    # Download YouTube video
    try:
        youtube = YouTube(url)
    except pytube_exceptions.RegexMatchError:
        print("The provided URL is not a valid YouTube URL.")
        return None
    try:
        video = youtube.streams.first()
        filename = video.default_filename
        video.download('/output')
        return os.path.join('/output', filename)
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None

def extract_audio(video):
    # Extract audio from video
    try:
        audio = AudioFileClip(video)
    except moviepy.editor.VideoFileClip.VideoFileClipError:
        print("The provided video file could not be opened.")
        return None
    try:
        duration = audio.duration
        chunk_length = 30  # length of each chunk in seconds
        chunks = []
        for i in range(0, int(duration), chunk_length):
            start = i
            end = i + chunk_length if i + chunk_length < duration else duration
            chunk = audio.subclip(start, end)
            chunk_file_path = f'/chunk_{i}.wav'
            chunk.write_audiofile(chunk_file_path, codec='pcm_s16le')
            chunks.append(chunk_file_path)
        return chunks
    except Exception as e:
        print(f"Error extracting audio: {e}")
        return None

def transcribe_audio(chunks):
    # Transcribe audio using Whisper API
    transcriptions = []
    for chunk in chunks:
        try:
            with open(chunk, 'rb') as audio_file:
                response = openai.Audio.transcribe("whisper-1", audio_file)
            if 'text' in response:
                transcriptions.append(response['text'])
            else:
                print(f"No transcription returned for audio chunk {chunk}. Response: {response}")
        except openai.error.OpenAIError as e:
            print(f"Error transcribing audio chunk {chunk}: {e}")
    transcription = " ".join(transcriptions)
    return transcription if transcription else None
def output_transcription(transcription):
    # Print transcription and save to file
    st.write(transcription)
    with open('transcription.txt', 'w') as file:
        file.write(transcription)

def cleanup(video, chunks):
    # Delete temporary files
    if os.path.exists(video):
        try:
            os.remove(video)
        except OSError as e:
            print(f"Error deleting video file: {e}")
    for chunk in chunks:
        if os.path.exists(chunk):
            try:
                os.remove(chunk)
            except OSError as e:
                print(f"Error deleting audio chunk {chunk}: {e}")

def main():
    url = get_youtube_url()
    video = download_video(url)
    if video is not None:
        audio = extract_audio(video)
        if audio is not None:
            transcription = transcribe_audio(audio)
            if transcription is not None:
                output_transcription(transcription)
                cleanup(video, audio)

if __name__ == "__main__":
    main()
