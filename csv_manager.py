#This module will be used to save reports to csv.
import csv
import os
import logging

def save_similar_titles_to_csv(file_path, similar_titles):
    with open(file_path, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Title 1', 'Title 2', 'Similarity', 'Link 1', 'Link 2'])
        for title1, title2, similarity, link1, link2 in similar_titles:
            csv_writer.writerow([title1, title2, similarity, link1, link2])

def save_invalid_links_to_csv(file_path, invalid_links):
    with open(file_path, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Link', 'Reason'])
        for link, reason in invalid_links:
            csv_writer.writerow([link, reason])
def save_playlist_to_csv(file_path, saved_video_links, video_titles):
    with open(file_path, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Title', 'Link'])
        for link, title in zip(saved_video_links, video_titles):
            csv_writer.writerow([title, link])
# Define the data structure for a song
class Song:
    def __init__(self, title, url, similarity=None):
        self.title = title
        self.url = url
        self.similarity = similarity

# Function to read data from CSV file and create a list of Song objects
def read_duplicate_songs_from_csv(filename):
    songs = []
    with open(filename, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        for row in reader:
            title1, title2, similarity, url1, url2 = row
            song1 = Song(title1.strip(), url1.strip())
            song2 = Song(title2.strip(), url2.strip(), similarity.strip())
            songs.append((song1, song2))
    return songs

def read_songs_from_csv(filename):
    songs = []
    with open(filename, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        for row in reader:
            title, url = row
            song = Song(title.strip(), url.strip())
            songs.append((song))
    return songs

def sanitize_title(title):
    return title.replace(',', '-')

def update_downloaded_list_csv_report(csv_file_path, url, downloaded_file):

    # Ensure directory for the CSV file exists
    csv_dir = os.path.dirname(csv_file_path)
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)

    # Check if the CSV file exists
    file_exists = os.path.isfile(csv_file_path)
    
    # Sanitize the downloaded file name
    sanitized_file = sanitize_title(downloaded_file)

    # Write or append to the CSV file
    with open(csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['URL', 'Downloaded File']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()  # File doesn't exist yet, write a header

        writer.writerow({'URL': url, 'Downloaded File': sanitized_file})
        
    logging.debug(f'Added {sanitized_file} to {csv_file_path}')

def read_links_from_csv(csv_file_path):
    links = []
    if os.path.isfile(csv_file_path):
        with open(csv_file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                if row:
                    links.append(row[0])
    return links

def subtract_links(links, csv_file_path):
    csv_links = read_links_from_csv(csv_file_path)
    result_links = [link for link in links if link not in csv_links]
    return result_links