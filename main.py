# Import necessary libraries
import re
import difflib
import yt_dlp
from tqdm import tqdm
import configparser
import time
from datetime import datetime
import logging
import os
import platform
import subprocess
import argparse
from csv_manager import (
    save_similar_titles_to_csv,
    save_playlist_to_csv,
    read_duplicate_songs_from_csv,
    read_songs_from_csv,
    update_downloaded_list_csv_report,
    subtract_links,
)
from html_manager import (
    extract_head_and_body,
    read_html_template,
    generate_html_duplicate_list,
    generate_html_list,
    load_js_code_from_file,
)
from mySQL_manager import create_database, add_report

# Define utility functions
def open_file(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        try:
            subprocess.Popen(["xdg-open", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except FileNotFoundError:
            logging.error(f"xdg-open not found. Please install it to open files: {path}")
            return
    
    print(f"Opening {path}")
    logging.debug(f'Opening {path}')

def create_folder_if_none(path):
    if not os.path.exists(path):
        os.makedirs(path)

def uniquify(path):
    filename, extension = os.path.splitext(path)
    counter = 1
    new_path = path
    while (os.path.exists(new_path)):
        new_path = f"{filename} ({counter}){extension}"
        counter += 1
    return new_path

def download_video(url, folder, csv_file_path):
    create_folder_if_none(folder)
    
    ydl_opts = {
        'noprogress': True,
        'quiet': True,
        'format': 'mp4',
        'outtmpl': os.path.join(folder, '%(title)s.%(ext)s')
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        title = info_dict.get('title', None)
        ext = 'mp4'
        downloaded_file = f"{title}.{ext}" if title else 'unknown_file'
    
    update_downloaded_list_csv_report(csv_file_path, url, downloaded_file)

def download_audio(url, con_extension, folder, csv_file_path):
    print(folder)
    create_folder_if_none(folder)
    ydl_opts = {
        'noprogress': True,    
        'quiet': True,        
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': con_extension.replace('.', ''),
            'preferredquality': '192',
        }]
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        info_dict = ydl.extract_info(url, download=True)
        title = info_dict.get('title', None)
        ext = con_extension.replace('.', '')
        downloaded_file = f"{title}.{ext}" if title else 'unknown_file'

    update_downloaded_list_csv_report(csv_file_path, url, downloaded_file)


def get_similar_titles(title1, title2):
    title1_clean = re.sub(r'[^\w\s]', '', title1.lower())
    title2_clean = re.sub(r'[^\w\s]', '', title2.lower())
    ratio = difflib.SequenceMatcher(None, title1_clean, title2_clean).ratio()
    return round(ratio, 2)

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
resume_downloads= int(config.get('main', 'resume_playlist_download'))

# MySQL zone
host=str(config.get('database', 'host'))
user=str(config.get('database', 'user'))
password=str(config.get('database', 'password'))
database=str(config.get('database', 'database'))
use_database=can_download_video = int(config.get('main', 'use_database'))

# Set up argument parser
parser = argparse.ArgumentParser(description='YTPO by Sebastian Legieziński')
parser.add_argument('--playlistURL', type=str, help='YouTube playlist link')
args = parser.parse_args()

# Get playlist link from user or argument
playlist_link = args.playlistURL if args.playlistURL else input("Enter YouTube playlist link: ")

# Fetch playlist details using yt-dlp
ydl_opts = {
    'quiet': True,
    'extract_flat': True,
    'dump_single_json': True,
    'skip_download': True
}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    playlist_dict = ydl.extract_info(playlist_link, download=False)

playlist_name = playlist_dict['title']
playlist_save_csv = f"{today}_{playlist_name}.csv"
video_entries = playlist_dict['entries']
database_file = f"Output/{playlist_name}"
create_folder_if_none(f"Output/{playlist_name}")

# Process playlist videos
video_titles = []
saved_video_links = []
invalid_video_links = []
start = time.time()

for entry in tqdm(video_entries, desc="Processing playlist videos"):
    try:
        video_title = entry['title']
        video_url = entry['url']
        video_titles.append(video_title)
        saved_video_links.append(video_url)
    except Exception as e:
        invalid_video_links.append((entry['url'], str(e)))
        logging.error(f"Invalid link: {entry['url']} -- {e}")

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
        logging.info('Saving similar titles to .csv...')
        print("Saving similar titles to .csv...")
        save_similar_titles_to_csv(f"Output/{playlist_name}/similar_titles.csv", similar_titles)
        # Load .css content
        css_file_path = 'web_template/style_template.css'
        with open(css_file_path, 'r', encoding='utf-8') as css_file:
            css_styles = css_file.read()
        logging.info('Saving similar titles to .html (This may take a while)...')
        print("Saving similar titles to .html (This may take a while)...")
        songs = read_duplicate_songs_from_csv(f"Output/{playlist_name}/similar_titles.csv")
        # Generate HTML content
        html_list = generate_html_duplicate_list(songs, playlist_name, playlist_link)
        # Read HTML template
        html_template = read_html_template('web_template/html_template_similar_report.html')
        # Extract head and body from HTML template
        head, body = extract_head_and_body(html_template)
        # Define page title based on playlist_name variable
        page_title = f"Similar Videos for Playlist: {playlist_name}"
        # Load JS code
        js_code=load_js_code_from_file('web_template/script_head_template.js')
        # Combine everything into a complete HTML structure with custom page title and CSS styles
        final_html = f"<html><head><title>{page_title}</title><script>{js_code}</script>{head}<style>{css_styles}</style></head><body>{body}{html_list}<footer><h3>Authors:</h3><div class='links'><a href='https://github.com/Kordight'><strong>Kordight</strong></a></div></footer></body></html>"
        # Write final HTML to file
        with open(f"Output/{playlist_name}/similar_videos.html", "w", encoding="utf-8") as outfile:
            outfile.write(final_html)

else:
    print(f"No similar titles found.")

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
        csv_file_path_audio = os.path.join('Output', playlist_name, 'Music', 'downloaded.csv')
        if resume_downloads == 1:
            video_links_to_download=subtract_links(saved_video_links, csv_file_path_audio)
            if len(saved_video_links) != len(video_links_to_download) and len(video_links_to_download) != 0:
                print(f"Resuming download.")
                logging.debug(f"Resuming download.")
            elif len(video_links_to_download) == 0:
                print(f"No (new) files to download.")
                logging.debug(f"No (new) files to download.")

        else:
             video_links_to_download=saved_video_links
        print(f"Downloading {len(video_links_to_download)} audio file(s).")
        logging.debug(f"Downloading {len(video_links_to_download)} audio file(s).")
        downloaded_files = 0
        wrong_links = []
        for link in tqdm(video_links_to_download, desc="Downloading audio files"):
            try:
                con_extension = ".wav" if download_wav == 1 else ".mp3"
                download_audio(link, con_extension, f"Output/{playlist_name}/Music", csv_file_path_audio)
                downloaded_files += 1
                logging.info(f"Downloaded audio: {link}")
            except Exception as e:
                wrong_links.append((link, str(e)))
                logging.error(f"Can't download: {link} -- {e}")

        print(f"Downloaded {downloaded_files} audio file(s).")
        logging.debug(f"Downloaded {downloaded_files} audio file(s).")
        if wrong_links:
            print(f"Couldn't download {len(wrong_links)} file(s).")
            for link, reason in wrong_links:
                print(f"{link} : {reason}")
        open_file(f"Output/{playlist_name}/Music")

    if can_download_video == 1:
        csv_file_path_video = os.path.join('Output', playlist_name, 'Videos', 'downloaded.csv')
        print(f'CSV path for video is: {csv_file_path_video}')
        if resume_downloads == 1:
            video_links_to_download=subtract_links(saved_video_links, csv_file_path_video)
            if len(saved_video_links) != len(video_links_to_download) and len(video_links_to_download) != 0:
                print(f"Resuming download.")
                logging.debug(f"Resuming download.")
            elif len(video_links_to_download) == 0:
                print(f"No (new) files to download.")
                logging.debug(f"No (new) files to download.")
        else:
             video_links_to_download=saved_video_links
        print(f"Downloading {len(video_links_to_download)} video file(s).")
        logging.debug(f"Downloading {len(video_links_to_download)} video file(s).")
        downloaded_files = 0
        wrong_links = []
        for link in tqdm(video_links_to_download, desc="Downloading video files"):
            try:
                download_video(link, f"Output/{playlist_name}/Videos", csv_file_path_video)
                downloaded_files += 1
                logging.info(f"Downloaded video: {link}")
            except Exception as e:
                wrong_links.append((link, str(e)))
                logging.error(f"Can't download: {link} -- {e}")

        print(f"Downloaded {downloaded_files} video file(s).")
        logging.debug(f"Downloaded {downloaded_files} video file(s).")
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
        with open(f"Output/{playlist_name}/{playlist_save_csv}", "w", encoding='utf-8') as file:
            file.write("Videos in playlist:\n")
            for title, link in zip(video_titles, saved_video_links):
                file.write(f"{title}     {link}\n")
    else:
        save_playlist_to_csv(f"Output/{playlist_name}/{playlist_save_csv}", saved_video_links, video_titles)

        # Load .css content
        css_file_path = 'web_template/style_template.css'
        with open(css_file_path, 'r', encoding='utf-8') as css_file:
            css_styles = css_file.read()
        logging.info('Saving playlist report to .html (This may take a while)...')
        print("Saving playlist report to .html (This may take a while)...")
        # Read data from CSV file
        songs = read_songs_from_csv(f"Output/{playlist_name}/{playlist_save_csv}")
        # Generate HTML content
        html_list = generate_html_list(songs, playlist_name, playlist_link)
        # Read HTML template
        html_template = read_html_template('web_template/html_template_backup_report.html')
        # Extract head and body from HTML template
        head, body = extract_head_and_body(html_template)
        # Define page title based on playlist_name variable
        page_title = f"Videos for Playlist: {playlist_name}"
        # Load JS template
        js_code=load_js_code_from_file('web_template/script_head_template.js')
        # Combine everything into a complete HTML structure with custom page title and CSS styles
        final_html = f"<html><head><title>{page_title}</title><script>{js_code}</script>{head}<style>{css_styles}</style></head><body>{body}{html_list}<footer><h3>Authors:</h3><div class='links'><a href='https://github.com/Kordight'><strong>Kordight</strong></a></div></footer></body></html>"
        # Write final HTML to file
        with open(f"Output/{playlist_name}/playlist_backup_latest.html", "w", encoding="utf-8") as outfile:
            outfile.write(final_html)
        with open(f"Output/{playlist_name}/{today}_playlist_backup.html", "w", encoding="utf-8") as outfile:
            outfile.write(final_html)
        if use_database == 1:
            create_database(host,user,password, database)
            add_report(host,user,password, database,video_titles,saved_video_links, playlist_name)
print("Done.")
