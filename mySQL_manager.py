import mysql.connector
from mysql.connector import Error
from datetime import datetime

def create_database(host, user, password, database):
    conn = None  # Initialize conn to None
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=3306
        )
        if conn.is_connected():
            cursor = conn.cursor()

            # Create tables if not exists
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS ytp_playlists (
                playlist_id INT AUTO_INCREMENT PRIMARY KEY,
                playlist_name VARCHAR(255),
                playlist_url VARCHAR(255) UNIQUE
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS ytp_videos (
                video_id INT AUTO_INCREMENT PRIMARY KEY,
                video_title VARCHAR(255),
                video_url VARCHAR(255) UNIQUE,
                video_length INT
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS ytp_reports (
                report_id INT AUTO_INCREMENT PRIMARY KEY,
                report_date DATE,
                playlist_id INT,
                FOREIGN KEY (playlist_id) REFERENCES ytp_playlists(playlist_id)
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS ytp_report_details (
                detail_id INT AUTO_INCREMENT PRIMARY KEY,
                report_id INT,
                video_id INT,
                FOREIGN KEY (report_id) REFERENCES ytp_reports(report_id),
                FOREIGN KEY (video_id) REFERENCES ytp_videos(video_id)
            )
            ''')

            conn.commit()
            
    except Error as e:
        print(f"Error: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def add_report(host, user, password, database, video_titles, saved_video_links, playlist_name, playlist_url, video_durations):
    conn = None  # Initialize conn to None
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=3306
        )
        if conn.is_connected():
            cursor = conn.cursor()

            # Check if playlist already exists
            cursor.execute('''
            SELECT playlist_id FROM ytp_playlists WHERE playlist_url = %s
            ''', (playlist_url,))
            result = cursor.fetchone()

            if result:
                playlist_id = result[0]
            else:
                # Add playlist
                cursor.execute('''
                INSERT INTO ytp_playlists (playlist_name, playlist_url)
                VALUES (%s, %s)
                ''', (playlist_name, playlist_url))
                conn.commit()  # Commit after inserting the playlist
                playlist_id = cursor.lastrowid

            # Add report
            report_date = datetime.today().strftime('%Y-%m-%d')
            cursor.execute('''
            INSERT INTO ytp_reports (report_date, playlist_id)
            VALUES (%s, %s)
            ''', (report_date, playlist_id))
            report_id = cursor.lastrowid

            # Add videos and report details
            for title, link, length in zip(video_titles, saved_video_links, video_durations):
                # Check if video already exists
                cursor.execute('''
                SELECT video_id FROM ytp_videos WHERE video_url = %s
                ''', (link,))
                video_result = cursor.fetchone()

                if video_result:
                    video_id = video_result[0]
                else:
                    # Add video
                    cursor.execute('''
                    INSERT INTO ytp_videos (video_title, video_url, video_length)
                    VALUES (%s, %s, %s)
                    ''', (title, link, length))
                    video_id = cursor.lastrowid

                # Add report detail
                cursor.execute('''
                INSERT INTO ytp_report_details (report_id, video_id)
                VALUES (%s, %s)
                ''', (report_id, video_id))

            conn.commit()
    except Error as e:
        print(f"Error: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
