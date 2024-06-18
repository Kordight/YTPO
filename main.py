# Import libraries
import re
import difflib
from pytube import YouTube, Playlist
from moviepy.editor import *
from moviepy.video.io.VideoFileClip import VideoFileClip
from tqdm import tqdm
import configparser
import time
from datetime import datetime
import logging
import os
import platform
import subprocess
from csv_manager import save_similar_titles_to_csv, save_playlist_to_csv

# Define functions
def open_file(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])
    print(f"Opening {path}")
    logging.debug(f'Opening {path}')

def create_folder_if_none(path):
    if not os.path.exists(path):
        os.makedirs(path)

def uniquify(path):
    filename, extension = os.path.splitext(path)
    counter = 1
    new_path = path
    while os.path.exists(new_path):
        new_path = f"{filename} ({counter}){extension}"
        counter += 1
    return new_path

def download_video(url, folder):
    yt = YouTube(url)
    video = yt.streams.filter(file_extension='mp4').first()
    if not os.path.exists(folder):
        os.makedirs(folder)
    path_mp4 = uniquify(os.path.join(folder, video.default_filename))
    video.download(output_path="", filename=path_mp4)

def download_audio(url, con_extension, folder):
    yt = YouTube(url)
    audio = yt.streams.filter(file_extension='mp4').first()
    if not os.path.exists(folder):
        os.makedirs(folder)
    path_mp3 = uniquify(os.path.join(folder, audio.default_filename.replace("temp_", "").replace(".mp4", con_extension)))
    audio.download(folder, filename=audio.default_filename)
    video = VideoFileClip(os.path.join(folder, audio.default_filename))
    video.audio.write_audiofile(path_mp3, verbose=False)
    video.close()
    os.remove(os.path.join(folder, audio.default_filename))

def get_similar_titles(title1, title2):
    title1_clean = re.sub(r'[^\w\s]', '', title1.lower())
    title2_clean = re.sub(r'[^\w\s]', '', title2.lower())
    ratio = difflib.SequenceMatcher(None, title1_clean, title2_clean).ratio()
    return ratio

# Set up logging and configuration
create_folder_if_none("Logs")
create_folder_if_none("Output")

today = datetime.today().strftime("%H-%M_%Y-%m-%d")
logging.basicConfig(filename=f'Logs/{today}_YTPO.log', encoding='utf-8', level=logging.DEBUG)
print(f"The log file is known as: {today}_YTPO.log")

config = configparser.ConfigParser()
config.read('config.ini')

min_similarity = float(config.get('main', 'min_similarity'))
can_download_video = int(config.get('main', 'download_video'))
can_download_music = int(config.get('main', 'download_music'))
backup_playlist = int(config.get('main', 'backup_playlist'))
download_wav = int(config.get('main', 'download_wav'))
use_csv = int(config.get('main', 'use_csv_file'))

# Get playlist link from user
print("YTPO by Sebastian Legieziński (seba0456)")
playlist_link = input("Enter YouTube playlist link: ")
playlist = Playlist(playlist_link)
playlist_name = playlist.title
playlist_save = f"{playlist_name}_{today}.txt"
playlist_save_csv = f"{playlist_name}_{today}.csv"
video_links = playlist.video_urls

create_folder_if_none(f"Output/{playlist_name}")

# Process playlist videos
video_titles = []
saved_video_links = []
invalid_video_links = []
start = time.time()

for link in tqdm(video_links, desc="Processing playlist videos"):
    try:
        video_title = YouTube(link).title
        video_titles.append(video_title)
        saved_video_links.append(link)
    except Exception as e:
        invalid_video_links.append((link, str(e)))
        logging.error(f"Invalid link: {link} -- {e}")

print(f'Time taken: {time.time() - start:.2f} seconds')
print("Comparing titles...")

# Compare video titles for similarity
similar_titles = []
for i in tqdm(range(len(video_titles)), desc="Comparing titles"):
    for j in range(i + 1, len(video_titles)):
        similarity = get_similar_titles(video_titles[i], video_titles[j])
        if similarity >= min_similarity:
            similar_titles.append((video_titles[i], video_titles[j], similarity, saved_video_links[i], saved_video_links[j]))

# Save similar titles
logging.info('Running get_similar_titles')
similar_titles = sorted(similar_titles, key=lambda x: x[2], reverse=True)

if similar_titles:
    print(f"Found {len(similar_titles)} similar titles.")
    if use_csv == 0:
        logging.info('Saving similar titles to .txt')
        with open(f"Output/{playlist_name}/similar_titles.txt", "w", encoding='utf-8') as file:
            file.write("Titles that are very similar:\n")
            for title1, title2, similarity, link1, link2 in similar_titles:
                file.write(f'{title1} and {title2}, similarity: {similarity:.2f}, {link1}, to {link2}\n')
    else:
        logging.info('Saving similar titles to .csv')
        save_similar_titles_to_csv(f"Output/{playlist_name}/similar_titles.csv", similar_titles)
else:
    print('No similar titles found.')

# Save invalid links
if invalid_video_links:
    print(f"Found {len(invalid_video_links)} invalid video links, saving them to invalid_links.txt")
    with open(f"Output/{playlist_name}/invalid_links.txt", "w", encoding='utf-8') as file:
        file.write("Links that are invalid:\n")
        for link, reason in invalid_video_links:
            file.write(f"{link} : {reason}\n")

# Download videos and audio
if can_download_video == 1 or can_download_music == 1:
    if can_download_music == 1:
        print(f"Downloading {len(saved_video_links)} audio file(s).")
        downloaded_files = 0
        wrong_links = []
        for link in tqdm(saved_video_links, desc="Downloading audio files"):
            try:
                con_extension = ".wav" if download_wav == 1 else ".mp3"
                download_audio(link, con_extension, f"Output/{playlist_name}/Music")
                downloaded_files += 1
                logging.info(f"Downloaded audio: {link}")
            except Exception as e:
                wrong_links.append((link, str(e)))
                logging.error(f"Can't download: {link} -- {e}")
        
        print(f"Downloaded {downloaded_files} audio file(s).")
        if wrong_links:
            print(f"Couldn't download {len(wrong_links)} file(s).")
            for link, reason in wrong_links:
                print(f"{link} : {reason}")
        open_file(f"Output/{playlist_name}/Music")

    if can_download_video == 1:
        print(f"Downloading {len(saved_video_links)} video file(s).")
        downloaded_files = 0
        wrong_links = []
        for link in tqdm(saved_video_links, desc="Downloading video files"):
            try:
                download_video(link, f"Output/{playlist_name}/Videos")
                downloaded_files += 1
                logging.info(f"Downloaded video: {link}")
            except Exception as e:
                wrong_links.append((link, str(e)))
                logging.error(f"Can't download: {link} -- {e}")
        
        print(f"Downloaded {downloaded_files} video file(s).")
        if wrong_links:
            print(f"Couldn't download {len(wrong_links)} file(s).")
            for link, reason in wrong_links:
                print(f"{link} : {reason}")
        open_file(f"Output/{playlist_name}/Videos")

# Saving playlist content
if backup_playlist == 1:
    print("Creating playlist backup...")
    if use_csv == 0:
        logging.info('Creating playlist backup...')
        with open(f"Output/{playlist_name}/{playlist_save}", "w", encoding='utf-8') as file:
            file.write("Videos in playlist:\n")
            for title, link in zip(video_titles, saved_video_links):
                file.write(f"{title}     {link}\n")
    else:
        save_playlist_to_csv(f"Output/{playlist_name}/{playlist_save_csv}", saved_video_links, video_titles)

print("Done.")
input("Press Enter to continue...")
