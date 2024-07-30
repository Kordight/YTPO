
Compare 2 reports to see what changed in the playlist.

```sql

SELECT 
    d1.video_title AS title, 
    d1.video_url AS link, 
    r1.playlist_name AS playlist_name, 
    'removed' AS status
FROM 
    reports r1
JOIN 
    report_details d1 
ON 
    r1.report_id = d1.report_id 
WHERE 
    r1.report_id = 1 
    AND d1.video_title NOT IN (SELECT d2.video_title FROM report_details d2 WHERE d2.report_id = 2)

UNION ALL


SELECT 
    d2.video_title AS title, 
    d2.video_url AS link, 
    r2.playlist_name AS playlist_name, 
    'added' AS status
FROM 
    reports r2
JOIN 
    report_details d2 
ON 
    r2.report_id = d2.report_id 
WHERE 
    r2.report_id = 2 
    AND d2.video_title NOT IN (SELECT d1.video_title FROM report_details d1 WHERE d1.report_id = 1)

ORDER BY title;

```