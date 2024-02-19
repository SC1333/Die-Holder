<?php
// Start the session
session_start();

// Retrieve the user ID from the session cookie
$userID = $_SESSION['user_id'];

// Pass the user ID to JavaScript
echo "<script>var userID = $userID;</script>";
?>