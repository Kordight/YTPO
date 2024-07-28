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
            CREATE TABLE IF NOT EXISTS reports (
                report_id INT AUTO_INCREMENT PRIMARY KEY,
                report_date DATE,
                playlist_name VARCHAR(255)
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS report_details (
                detail_id INT AUTO_INCREMENT PRIMARY KEY,
                report_id INT,
                video_title VARCHAR(255),
                video_url VARCHAR(255),
                FOREIGN KEY (report_id) REFERENCES reports(report_id)
            )
            ''')

            conn.commit()
            
    except Error as e:
        print(f"Error: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def add_report(host, user, password, database, video_titles, saved_video_links, playlist_name):
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

            # Add report
            report_date = datetime.today().strftime('%Y-%m-%d')
            cursor.execute('''
            INSERT INTO reports (report_date, playlist_name)
            VALUES (%s, %s)
            ''', (report_date, playlist_name))
            report_id = cursor.lastrowid

            # Add report details
            for title, link in zip(video_titles, saved_video_links):
                cursor.execute('''
                INSERT INTO report_details (report_id, video_title, video_url)
                VALUES (%s, %s, %s)
                ''', (report_id, title, link))

            conn.commit()
    except Error as e:
        print(f"Error: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
