#Import libraries
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
import random
import os
import platform
import subprocess
#Get session ID
def gen_random_hex_string(size):
    return ''.join(random.choices('0123456789abcdef', k=size))
#Open file
def open_file(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])
    print("Opening " + str(path))
    logging.debug('Opening '+path)

today = datetime.today().strftime("%Y-%m-%d")
session = gen_random_hex_string(6)
logging.basicConfig(filename=today+"_"+session+'_YTPO.log', encoding='utf-8', level=logging.DEBUG)
#Reading variables from .ini
logging.debug('Reading data from ini...')
config = configparser.ConfigParser()
config.read('config.ini')
min_similarity = float(config.get('main', 'min_similarity'))
logging.debug('min_similarity is: '+str(min_similarity))
can_download_video=int(config.get('main', 'download_video'))
logging.debug('can_download_video is: '+str(can_download_video))
can_download_music=int(config.get('main', 'download_music'))
logging.debug('can_download_music is: '+str(can_download_music))
backup_playlist=int(config.get('main', 'backup_playlist'))
logging.debug('backup_playlist is: '+str(backup_playlist))
download_wav=int(config.get('main', 'download_wav'))
logging.debug('download_wav is: '+str(backup_playlist))
print("YTPO by Sebastian Legieziński (seba0456)")
print("Session ID: "+session)
playlist_link = input("Enter YouTube playlist link:")
p=Playlist(playlist_link)
playlist_name=p.title
playlist_save = f"{playlist_name}_{today}.txt"
playlist = Playlist(playlist_link)
print("Opening", playlist_name)
logging.info('Playlist is: ' + playlist_link + '. Playlist name is: '+playlist_name)
video_links = Playlist(playlist_link).video_urls
#Unique filename
def uniquify(path):
    filename, extension = os.path.splitext(path)
    counter = 1

    while os.path.exists(path):

        path = filename + " (" + str(counter) + ")"
        counter += 1

    return os.path.splitext(path)[0]

#Functions for downloading from YouTube
def download_video(url, folder='Videos'):
    yt = YouTube(url)
    video = yt.streams.filter(file_extension='mp4').first()
    if not os.path.exists(folder):
        os.makedirs(folder)
    i = 1
    file_name = video.default_filename
    path_mp4 = os.path.join(folder, file_name)
    video.download(output_path="", filename=uniquify(path_mp4)+'.mp4')

def download_audio(url, con_extension, folder='Music'):
    yt = YouTube(url)
    audio = yt.streams.filter(file_extension='mp4').first()
    if not os.path.exists(folder):
        os.makedirs(folder)
    file_name = audio.default_filename
    path_mp3 = os.path.join(folder, file_name.replace("temp_", "").replace(".mp4", "") + str(con_extension))
    filename, extension = os.path.splitext(path_mp3)
    i = 1
    while os.path.exists(path_mp3):
        path_mp3 = filename  + " (" + str(i) + ")" + extension
        i += 1
        
    audio.download(folder, filename=file_name)
    video = VideoFileClip(os.path.join(folder, file_name))
    video.audio.write_audiofile(os.path.join(path_mp3),verbose=False)
    video.close()
    video= None
    os.remove(os.path.join(folder, file_name))

#Function for comparing titles
def get_similar_titles(title1, title2, link1,link2):
    title1 = re.sub(r'[^\w\s]', '', title1.lower())
    title2 = re.sub(r'[^\w\s]', '', title2.lower())
    ratio = difflib.SequenceMatcher(None, title1, title2).ratio()
    return ratio

video_titles = []
saved_video_links = []
invalid_video_links = []
start = time.time()
#reading playlist
for link in tqdm(video_links):
    try:
        video_title = YouTube(link).title
        video_titles.append(video_title)
        saved_video_links.append(link)
    except Exception as e:
        invalid_video_links.append((link, str(e)))
        logging.error("Invalid link: "+link + " -- "+ str(e))

print(f'Time taken: {time.time() - start}')
print("Comparing titles...")
similar_titles = []
for i in tqdm(range(len(video_titles))):
    for j in range(i+1, len(video_titles)):
        similarity = get_similar_titles(video_titles[i], video_titles[j], saved_video_links[i], saved_video_links[j])
        if similarity >= min_similarity:
            similar_titles.append((video_titles[i], video_titles[j], similarity, saved_video_links[i], saved_video_links[j]))
print(20*"_")
#Sorting & saving similar titles
logging.info('Running get_similar_titles')
similar_titles = sorted(similar_titles, key=lambda x: x[2], reverse=True)
if similar_titles:
    print("Comprising ", len(video_titles), ",", len(invalid_video_links), "title(s) are invalid.")
    print("Found ", len(similar_titles), "similar tiles, saving them to similar_titles.txt")
    with open("similar_titles.txt", "w", encoding='utf-8') as file:
        file.seek(0)
        file.truncate()
        file.write("Titles that are very similar:\n")
        for title1, title2, similarity, link1, link2 in similar_titles:
            file.write(f'{title1} and {title2}, similarity: {similarity:.2f}, {link1}, to {link2}\n')
else:
    print('No similar titles found.')
#Saving invalid links
if len(invalid_video_links) > 0:
    print("Found ", len(invalid_video_links), "invalid video links, saving them to invalid_links.txt")
    with open("Invalid_links.txt", "w", encoding='utf-8') as file:
        file.seek(0)
        file.truncate()
        file.write("Links that are invalid:\n")
        for i, reason in invalid_video_links:
            invalid_video_link=i+ " : "+ reason
            file.write(invalid_video_link+"\n")
print(20*"_")
#Downloading files
if can_download_video == 1 or can_download_music == 1:
    if can_download_music == 1:
        print("Downloading ", len(saved_video_links), "audio file(s).")
        downloaded_files = 0
        wrong_links = []
        for i in tqdm(saved_video_links):
            try:
                if download_wav == 0:
                    download_audio(i, con_extension=".mp3")
                elif download_wav == 1:
                    download_audio(i, con_extension=".wav")
                    print("Downloaded wav")
                downloaded_files += 1
                logging.info("Downloaded audio: "+i)
            except Exception as e: 
                wrong_links.append((i, str(e)))
                logging.error("Can't download: "+i + " -- " + str(e))
                continue
        print("Downloaded ", downloaded_files, "file(s).")
        if len(saved_video_links) != downloaded_files:
            print("Couldn't download ", len(saved_video_links) - downloaded_files, "file(s).")
            for link, reason in wrong_links:
                print(link, " : ", reason)
        print(20 * "_")
        open_file("Music")
    if can_download_video == 1:
        print("Downloading ", len(saved_video_links), "video file(s).")
        downloaded_files=0
        wrong_links=[]
        for i in tqdm(saved_video_links):
            try:
                download_video(i)
                downloaded_files+=1
                logging.info("Downloaded video: " + i)
            except Exception as e:
                wrong_links.append((i, str(e)))
                logging.error("Can't download: " + i + " -- " + str(e))
                continue
        print("Downloaded ", downloaded_files, "file(s).")
        if len(saved_video_links) != downloaded_files:
            print("Couldn't download ", len(saved_video_links)-downloaded_files, "file(s).")
            for link, reason in wrong_links:
                print(link, " : ", reason)
        open_file("Video")
        print(20 * "_")
#Saving playlist content
if backup_playlist == 1:
    print("Creating playlist backup...")
    logging.info('Creating playlist backup...')
    with open(playlist_save, "w", encoding='utf-8') as file:
        file.seek(0)
        file.truncate()
        file.write("Videos in playlist:\n")
        for saved_video_links, video_titles in zip(saved_video_links, video_titles):
            file.write(video_titles + (5 * " ") + saved_video_links + "\n")
print("Done.")
input("Press Enter to continue...")
