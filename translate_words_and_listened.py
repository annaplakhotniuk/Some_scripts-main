from gtts import gTTS
import os
import re
import time
from mtranslate import translate
from moviepy.editor import *
import cv2
import numpy as np
from pydub import AudioSegment

# Set the path to ImageMagick convert binary
os.environ["IMAGEIO_CONVERT_EXE"] = "/usr/bin/convert"

file_path = '/home/user/Documents/Setings/test.txt'

# Function to translate a word
def translate_word(word, dest='en'):
    translation = translate(word, dest)
    return translation

# Function to save text as speech audio file
def save_audio(text, file_path, lang='en'):
    tts = gTTS(text=text, lang=lang)
    tts.save(file_path)

# Read words from a text file
def read_words_from_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    words = []
    for line in lines:
        word = line.split('-')[0].strip()
        word = re.sub(r'\[.*?\]', '', word).strip()
        words.append(word)
    return words

def create_video(audio_files, output_file, words):
    clips = []
    audio_clips = []

    for i, word in enumerate(words):
        audio_file = audio_files[i]
        audio = AudioSegment.from_file(audio_file)

        # Load a blank image frame
        frame = np.zeros((400, 800, 3), dtype=np.uint8)

        # Add text overlay to the image frame
        font = cv2.FONT_HERSHEY_SIMPLEX
        text = word
        text_color = (255, 255, 255)  # white color
        text_position = (50, 200)
        text_thickness = 2
        text_size = 1
        cv2.putText(frame, text, text_position, font, text_size, text_color, text_thickness, cv2.LINE_AA)

        # Convert the image frame to a video clip
        duration = int(audio.duration_seconds * 1000)  # duration in milliseconds
        frame_clip = ImageSequenceClip([frame], durations=[duration / 1000])

        # Append the video clip to the clips list
        clips.append(frame_clip)

        # Append the audio clip to the audio_clips list
        audio_clips.append(audio)

    # Concatenate the video clips
    final_clip = concatenate_videoclips(clips)

    # Concatenate the audio clips
    final_audio = AudioSegment.empty()
    for clip in audio_clips:
        final_audio += clip

    # Set the audio for the final clip
    final_clip = final_clip.with_audio(final_audio)

    # Write the final video to the output file
    final_clip.write_videofile(output_file, codec='libx264', fps=30)

def concatenate_audio_files(audio_files, output_file):
    combined_audio = AudioSegment.silent(duration=0)
    _counter = 6
    for i, file in enumerate(audio_files, start=1):
        try:
            if i == _counter:
                _counter += 6
                audio = AudioSegment.from_file(file)
                combined_audio += audio
                audio += AudioSegment.silent(duration=3000)  # Add 1 second of silence after each repetition
            else:
                audio = AudioSegment.from_file(file)
                combined_audio += audio
        except Exception as e:
            print(f"Failed to open audio file: {file}\nError: {str(e)}")
    combined_audio.export(output_file, format='mp3')

def main(file_path):
    words = read_words_from_file(file_path)

    audio_files = []
    translations = {}
    for word in words:
        ukrainian_translation = translate_word(word, dest='uk')
        ukrainian_audio_file_path = f'{word}_translation_uk.mp3'
        save_audio(ukrainian_translation, ukrainian_audio_file_path, lang='uk')

        english_translation = translate_word(word)
        english_audio_file_path = f'{word}_translation_en.mp3'
        save_audio(english_translation, english_audio_file_path)

        for _ in range(0, 3):
            audio_files.append(ukrainian_audio_file_path)
            audio_files.append(english_audio_file_path)

        translations[word] = {
            english_translation: ukrainian_translation
        }

        with open('translations.txt', 'a') as file:
            for key, value in translations[word].items():
                file.write(f'{key}: {value}\n')
        print(f"Function main: write '{key}: {value}' in to 'translations.txt' file")
        time.sleep(0.5)

    concatenate_audio_files(audio_files, 'all3_translations.mp3')
    #create_video(audio_files, 'output.mp4', words)

if __name__ == '__main__':
    main(file_path=file_path)