<?php
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "muzyka";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);
// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$sql = "SELECT id, titleA, titleB, similarity, urlA, urlB FROM similar_titles";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    echo "<ol>";
    // output data of each row
    while ($row = $result->fetch_assoc()) {
        echo "<li><a href='" . $row["urlA"] . "'> " . $row["titleA"] . "</a> is similar to: <a href='" . $row["urlB"] . "'>" . $row["titleB"] . "</a> by: " . $row["similarity"] . "</li><br>";
    }
    echo "</ol>";
} else {
    echo "0 results";
}
$conn->close();
