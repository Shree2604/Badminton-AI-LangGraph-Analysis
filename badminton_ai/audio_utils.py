"""Audio extraction and transcription utilities."""
import os
import tempfile
import uuid
import speech_recognition as sr
from pathlib import Path
from typing import Optional, Tuple
import numpy as np
from pydub import AudioSegment
from pydub.silence import split_on_silence

def extract_audio(video_path: str, output_path: Optional[str] = None) -> str:
    """Extract audio from video file and save as WAV."""
    import uuid
    try:
        if output_path is None:
            output_path = os.path.join(tempfile.gettempdir(), f"audio_{uuid.uuid4()}.wav")
        
        print(f"Extracting audio from {video_path} to {output_path}")
        # Load video and extract audio
        video = AudioSegment.from_file(video_path)
        # Convert to mono and 16kHz to reduce size
        audio = video.set_channels(1).set_frame_rate(16000)
        audio.export(output_path, format="wav")
        return output_path
    except Exception as e:
        print(f"Error extracting audio: {str(e)}")
        if output_path and os.path.exists(output_path):
            try:
                os.unlink(output_path)
            except:
                pass
        raise

def transcribe(audio_path: str, language: str = "en-US") -> str:
    """Transcribe audio using Google's Web Speech API."""
    r = sr.Recognizer()
    folder_name = "audio-chunks"
    
    try:
        # Use pydub to handle the audio file
        sound = AudioSegment.from_wav(audio_path)
        
        # Split audio where silence is 700ms or more
        chunks = split_on_silence(
            sound,
            min_silence_len=500,
            silence_thresh=sound.dBFS-14,
            keep_silence=500
        )
        
        # Create a directory to store the audio chunks
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)
        
        whole_text = ""
        
        # Process each chunk
        for i, chunk in enumerate(chunks):
            # Export chunk and save it in the folder
            chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
            chunk.export(chunk_filename, format="wav")
            
            # Recognize the chunk
            with sr.AudioFile(chunk_filename) as source:
                audio_listened = r.record(source)
                try:
                    text = r.recognize_google(audio_listened, language=language)
                    whole_text += text + " "
                except (sr.UnknownValueError, sr.RequestError):
                    continue
            
            # Clean up the chunk file
            try:
                os.unlink(chunk_filename)
            except OSError:
                pass
        
        return whole_text.strip() if whole_text else "[No speech detected]"
        
    except Exception:
        return "[Transcription failed]"
    finally:
        # Clean up the chunks directory if it exists
        if os.path.exists(folder_name):
            try:
                # Remove all files in the directory
                for filename in os.listdir(folder_name):
                    file_path = os.path.join(folder_name, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            import shutil
                            shutil.rmtree(file_path, ignore_errors=True)
                    except OSError:
                        continue
                # Remove the directory itself
                os.rmdir(folder_name)
            except OSError:
                pass
        
        # Clean up the original audio file
        if os.path.exists(audio_path):
            try:
                os.unlink(audio_path)
            except OSError:
                pass

