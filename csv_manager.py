#This module will be used to save reports to csv.
import csv

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