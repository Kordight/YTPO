# What is YouTube Playlist Organizer?

YTPO is a program written with the help of the [Pytube](https://github.com/pytube/pytube) library. This script can list similar video titles, and invalid video links, and save a report in `.txt`, `.csv`, and user-friendly `.html` formats detailing what videos are in a playlist. YouTube Playlist Organizer can also download videos from a playlist and save them as mp3 or mp4 files.

![image](https://user-images.githubusercontent.com/46867564/216819827-3c7ed7b9-a2fd-4398-ad84-3d29a6bfb1d7.png)

## Setup

Download the `.zip` from GitHub or type:

```sh

git clone https://github.com/seba0456/YouTube-Playlist-Organizer
```

Then enter the project directory. In order to make it work, you need [tqdm](https://github.com/tqdm/tqdm), [Pytube](https://github.com/pytube/pytube), and [Moviepy](https://github.com/Zulko/moviepy). You can install them by typing in terminal/cmd:

```sh

pip install -r requirements.txt
```

Then you need to edit `config.ini`.

- `min_similarity=` determines the minimum similarity of titles to catch, default `0.75`, valid values: from `0` to `1`.

- `download_video=` enables or disables downloading videos from the playlist, default `0`, valid values: `0` or `1`.

- `download_music=` enables or disables downloading audio from the playlist, default `0`, valid values: `0` or `1`.

- `backup_playlist=` enables or disables saving all links and titles to a `.txt` file, default `0`, valid values: `0` or `1`.

- `download_wav=` enables or disables saving audio from the playlist as `.wav` files, default `0`, valid values: `0` or `1`.

- `use_csv_file=` enables or disables saving reports from the playlist as `.csv` and `.html` files, default `1`, valid values: `0` or `1`.

## Running the Program

You can run the program by opening CMD or Terminal and typing this command:

```sh

python3 main.py
```

Alternatively, you can run this command:

```sh

python main.py --playlistURL "https://youtube.com/playlist?list=YOUR_PLAYLIST_URL"
```

Without an argument, the program will ask for a playlist link. A valid link looks like this: `https://www.youtube.com/playlist?list=PLuoflVrROeM3MLY-78dZTsWnkZWextssm`. Then you have to wait for the program to finish its job. `.txt`, `.csv`, and `.html` reports can be found inside the `Output/{Playlist_name}` folder, audio files inside the `Output/{Playlist_name}/Music` folder, and `.mp4` files inside the `Output/{Playlist_name}/Videos` folder. These folders are available in the program directory.

## TXT Files Example

Keep in mind that `.txt` reports are deprecated. By default, `.html` and `.csv` reports will be generated.

**similar_titles.txt:**

> Titles that are very similar:
> Slendertubbies tutrial - How to host and join LAN server and Slendertubbies tutrial - How to host and join Steam server, similarity: 0.95, <https://www.youtube.com/watch?v=BU92f9TOzNI>, to <https://www.youtube.com/watch?v=apIwgZ7y3Aw>

**PlaylistBackup.txt:**

> Videos in playlist:
> Slendertubbies tutrial - How to install Slendertubbies from Gamejolt?     <https://www.youtube.com/watch?v=0INaIXDHMBE>
> Slendertubbies tutrial - How to host and join LAN server     <https://www.youtube.com/watch?v=BU92f9TOzNI>
>How to Install Steam on Windows 10     <https://www.youtube.com/watch?v=zX6eh5615bE>
>Slendertubbies tutrial - How to host and join Steam server     <https://www.youtube.com/watch?v=apIwgZ7y3Aw>

## Ideas how to use this script

1. You can download videos/audio from your favorite playlist.
2. You can track similar positions in your playlist.
3. You can run this script automatically and ensure that you will never lose video titles due to the original video deletion.
4. You can use the script to generate reports for playlist management, making it easier to organize and review content.
5. You can back up entire playlists, preserving links and titles in case of future changes or deletions on YouTube.
