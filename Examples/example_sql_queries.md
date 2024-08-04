# Example SQL queries

Since this program supports saving reports to MySQL, I'll post here some useful queries that you can use.
I'll do my best to improve these queries. Feel free to use them for your purposes.

## Compare 2 reports to see what changed in the playlist

Remember to replace `YOUR_PLAYLIST_URL` with playlist URL.

WITH playlist_info AS (
    SELECT playlist_id
    FROM ytp_playlists
    WHERE playlist_url = 'YOUR_PLAYLIST_URL'
),


last_two_reports AS (
    SELECT report_id
    FROM ytp_reports
    WHERE playlist_id = (SELECT playlist_id FROM playlist_info)
    ORDER BY report_date DESC
    LIMIT 2
),

report_videos AS (
    SELECT rvd.report_id, rvd.video_id
    FROM ytp_report_details rvd
    JOIN last_two_reports ltr ON rvd.report_id = ltr.report_id
),

added_videos AS (
    SELECT rv1.video_id
    FROM report_videos rv1
    WHERE rv1.report_id = (SELECT report_id FROM last_two_reports ORDER BY report_id DESC LIMIT 1)
    AND rv1.video_id NOT IN (
        SELECT rv2.video_id
        FROM report_videos rv2
        WHERE rv2.report_id = (SELECT report_id FROM last_two_reports ORDER BY report_id DESC LIMIT 1 OFFSET 1)
    )
),

removed_videos AS (
    SELECT rv2.video_id
    FROM report_videos rv2
    WHERE rv2.report_id = (SELECT report_id FROM last_two_reports ORDER BY report_id DESC LIMIT 1 OFFSET 1)
    AND rv2.video_id NOT IN (
        SELECT rv1.video_id
        FROM report_videos rv1
        WHERE rv1.report_id = (SELECT report_id FROM last_two_reports ORDER BY report_id DESC LIMIT 1)
    )
)

SELECT 'Added' AS action, v.video_title, v.video_url
FROM added_videos av
JOIN ytp_videos v ON av.video_id = v.video_id

UNION ALL

SELECT 'Removed' AS action, v.video_title, v.video_url
FROM removed_videos rv
JOIN ytp_videos v ON rv.video_id = v.video_id;

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
