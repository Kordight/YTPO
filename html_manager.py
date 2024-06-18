# Function to generate HTML code for the list of similar songs
def generate_html_list(songs):
    song_amount=len(songs)
    html_content = "<div class='border-box'><h1>Similar songs</h1><br><p>Found: " + str(song_amount) + " similar videos in this playlist.</p><br><ol>"
    for song1, song2 in songs:
        html_content += f"<li><a href='{song1.url}'>{song1.title}</a> is similar to: <a href='{song2.url}'>{song2.title}</a> by: {song2.similarity if song2.similarity else ''}</li><br>"
    html_content += "</ol></div>"
    return html_content

def read_html_template(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    return html_content

def extract_head_and_body(html_content):
    head_start = html_content.find('<head>') + len('<head>')
    head_end = html_content.find('</head>')
    body_start = html_content.find('<body>') + len('<body>')
    body_end = html_content.find('</body>')

    head = html_content[head_start:head_end].strip()
    body = html_content[body_start:body_end].strip()
    
    return head, body