# Example SQL queries

Since this program supports saving reports to MySQL, I'll post here some useful queries that you can use.
I'll do my best to improve these queries. Feel free to use them for your purposes.

## Compare 2 reports to see what changed in the playlist

Remember to replace `YOUR_PLAYLIST_URL` with playlist URL.

```sql

SELECT 
    v1.video_title AS title, 
    v1.video_url AS link, 
    p1.playlist_name AS playlist_name, 
    'removed' AS status
FROM 
    ytp_reports r1
JOIN 
    ytp_report_details rd1 ON r1.report_id = rd1.report_id
JOIN 
    ytp_videos v1 ON rd1.video_id = v1.video_id
JOIN 
    ytp_playlists p1 ON r1.playlist_id = p1.playlist_id
WHERE 
    r1.report_id = 1 
    AND v1.video_title NOT IN (
        SELECT v2.video_title 
        FROM ytp_reports r2
        JOIN ytp_report_details rd2 ON r2.report_id = rd2.report_id
        JOIN ytp_videos v2 ON rd2.video_id = v2.video_id
        WHERE r2.report_id = 2
    )

UNION ALL

SELECT 
    v2.video_title AS title, 
    v2.video_url AS link, 
    p2.playlist_name AS playlist_name, 
    'added' AS status
FROM 
    ytp_reports r2
JOIN 
    ytp_report_details rd2 ON r2.report_id = rd2.report_id
JOIN 
    ytp_videos v2 ON rd2.video_id = v2.video_id
JOIN 
    ytp_playlists p2 ON r2.playlist_id = p2.playlist_id
WHERE 
    r2.report_id = 2 
    AND v2.video_title NOT IN (
        SELECT v1.video_title 
        FROM ytp_reports r1
        JOIN ytp_report_details rd1 ON r1.report_id = rd1.report_id
        JOIN ytp_videos v1 ON rd1.video_id = v1.video_id
        WHERE r1.report_id = 1
    )

ORDER BY title;

```

## Compare first report with latest

Remember to replace `YOUR_PLAYLIST_URL` with playlist URL.

```sql

WITH LatestReports AS (
    SELECT 
        r.report_id
    FROM 
        ytp_reports r
    JOIN 
        ytp_playlists p ON r.playlist_id = p.playlist_id
    WHERE 
        p.playlist_url = 'YOUR_PLAYLIST_URL'
    ORDER BY 
        r.report_date DESC
    LIMIT 2
),
SecondLatestReport AS (
    SELECT 
        report_id 
    FROM 
        LatestReports 
    LIMIT 1 OFFSET 1
),
LatestReport AS (
    SELECT 
        report_id 
    FROM 
        LatestReports 
    LIMIT 1
)

SELECT 
    v1.video_title AS title, 
    v1.video_url AS link, 
    p1.playlist_name AS playlist_name, 
    'removed' AS status
FROM 
    ytp_reports r1
JOIN 
    ytp_report_details rd1 ON r1.report_id = rd1.report_id
JOIN 
    ytp_videos v1 ON rd1.video_id = v1.video_id
JOIN 
    ytp_playlists p1 ON r1.playlist_id = p1.playlist_id
WHERE 
    r1.report_id = (SELECT report_id FROM SecondLatestReport) 
    AND v1.video_title NOT IN (
        SELECT v2.video_title 
        FROM ytp_reports r2
        JOIN ytp_report_details rd2 ON r2.report_id = rd2.report_id
        JOIN ytp_videos v2 ON rd2.video_id = v2.video_id
        WHERE r2.report_id = (SELECT report_id FROM LatestReport)
    )

UNION ALL

SELECT 
    v2.video_title AS title, 
    v2.video_url AS link, 
    p2.playlist_name AS playlist_name, 
    'added' AS status
FROM 
    ytp_reports r2
JOIN 
    ytp_report_details rd2 ON r2.report_id = rd2.report_id
JOIN 
    ytp_videos v2 ON rd2.video_id = v2.video_id
JOIN 
    ytp_playlists p2 ON r2.playlist_id = p2.playlist_id
WHERE 
    r2.report_id = (SELECT report_id FROM LatestReport)
    AND v2.video_title NOT IN (
        SELECT v1.video_title 
        FROM ytp_reports r1
        JOIN ytp_report_details rd1 ON r1.report_id = rd1.report_id
        JOIN ytp_videos v1 ON rd1.video_id = v1.video_id
        WHERE r1.report_id = (SELECT report_id FROM SecondLatestReport)
    )

ORDER BY title;


```
