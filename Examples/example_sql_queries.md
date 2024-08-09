# Example SQL queries

Since this program supports saving reports to MySQL, I'll post here some useful queries that you can use.
I'll do my best to improve these queries. Feel free to use them for your purposes.

## List all videos for lates playlist report

Remember to replace `YOUR_PLAYLIST_URL` with playlist URL.

```sql
WITH LatestReport AS (
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
    LIMIT 1
)
SELECT 
    ROW_NUMBER() OVER (ORDER BY v.video_title) AS video_number,
    v.video_title, v.video_url
FROM 
    ytp_videos v
JOIN 
    ytp_report_details rd ON v.video_id = rd.video_id
JOIN 
    LatestReport lr ON rd.report_id = lr.report_id;

```

## Compare 2 reports to see what changed in the playlist

Remember to replace `YOUR_PLAYLIST_URL` with playlist URL.

```sql

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

WITH playlist_info AS (
    SELECT playlist_id
    FROM ytp_playlists
    WHERE playlist_url = 'YOUR_PLAYLIST_URL'
),

latest_report AS (
    SELECT report_id
    FROM ytp_reports
    WHERE playlist_id = (SELECT playlist_id FROM playlist_info)
    ORDER BY report_date DESC
    LIMIT 1
),

first_report AS (
    SELECT report_id
    FROM ytp_reports
    WHERE playlist_id = (SELECT playlist_id FROM playlist_info)
    ORDER BY report_id ASC
    LIMIT 1
),

latest_report_videos AS (
    SELECT rvd.video_id
    FROM ytp_report_details rvd
    JOIN latest_report lr ON rvd.report_id = lr.report_id
),

first_report_videos AS (
    SELECT rvd.video_id
    FROM ytp_report_details rvd
    JOIN first_report fr ON rvd.report_id = fr.report_id
),

added_videos AS (
    SELECT lv.video_id
    FROM latest_report_videos lv
    WHERE lv.video_id NOT IN (SELECT fv.video_id FROM first_report_videos fv)
),

removed_videos AS (
    SELECT fv.video_id
    FROM first_report_videos fv
    WHERE fv.video_id NOT IN (SELECT lv.video_id FROM latest_report_videos lv)
)

SELECT 'Added' AS action, v.video_title, v.video_url
FROM added_videos av
JOIN ytp_videos v ON av.video_id = v.video_id

UNION ALL

SELECT 'Removed' AS action, v.video_title, v.video_url
FROM removed_videos rv
JOIN ytp_videos v ON rv.video_id = v.video_id;

```
