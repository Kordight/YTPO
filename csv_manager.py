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
