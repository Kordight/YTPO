# What is YouTube Playlist Organizer?
YTPO is a program written with the help of [Pytube](https://github.com/pytube/pytube) library. This script can list similar video titles, invalid video links, save as .txt what videos are in playlist. YouTube Playlist Organizer can also download videos from playlist and save them as mp3 or mp4.
![image](https://user-images.githubusercontent.com/46867564/216819827-3c7ed7b9-a2fd-4398-ad84-3d29a6bfb1d7.png)

## Setup
Download `.zip` from GitHub or type 

`git clone https://github.com/seba0456/YouTube-Playlist-Organizer `

Then enter project directory 
In order to make it work, you need [tqdm](https://github.com/tqdm/tqdm) and [Pytube](https://github.com/pytube/pytube).
You can install them by typing in terminal/cmd
```
pip install -r requirements.txt
```
Then you need to edit `config.ini`.

`min_similarity=` determines minimum similarity of titles to catch, ex.`0.75`, valid value: from `0` to `1`.

`download_video=` enables or disables downloading videos from playlist, ex.`0`, valid value: `0` or `1`.

`download_music=` enables or disables downloading audio from playlist, ex.`0`, valid value: `0` or `1`.

`backup_playlist=` enables or disables saving all links and title to `.txt` file, ex.`0`, valid value: `0` or `1`.
### Running program
You can run the program by opening CMD or Terminal and typing this command:
`python3 main.py`

Program will ask for playlist link, valid link looks like this `https://www.youtube.com/playlist?list=PLuoflVrROeM3MLY-78dZTsWnkZWextssm`. Then you have to wait for the program to finish its job. 
`.txt` can be found in program directory, `.mp3` files inside `Music` folder, `.mp4` files inside `Videos`. These folders are available in program directory.
## TXT files example
similar_titles.txt:

```
Titles that are very similar:
Slendertubbies tutrial - How to host and join LAN server and Slendertubbies tutrial - How to host and join Steam server, similarity: 0.95, https://www.youtube.com/watch?v=BU92f9TOzNI, to https://www.youtube.com/watch?v=apIwgZ7y3Aw
```

PlaylistBackup.txt

```
Videos in playlist:
Slendertubbies tutrial - How to install Slendertubbies from Gamejolt?     https://www.youtube.com/watch?v=0INaIXDHMBE
Slendertubbies tutrial - How to host and join LAN server     https://www.youtube.com/watch?v=BU92f9TOzNI
How to Install Steam on Windows 10     https://www.youtube.com/watch?v=zX6eh5615bE
Slendertubbies tutrial - How to host and join Steam server     https://www.youtube.com/watch?v=apIwgZ7y3Aw
```
