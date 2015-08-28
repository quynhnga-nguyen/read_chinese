<?php
$pdo = new PDO('mysql:host=learn-chinese.cloudapp.net;port=3306;dbname=chinese_lang',
	'nga', 'Chinaman50100');
$pdo->exec("SET NAMES utf8");
$query = $pdo->prepare("SELECT text, difficulty FROM paragraph ORDER BY RAND() LIMIT 1");
$query->execute();
$result = $query->fetch(PDO::FETCH_ASSOC);
?>

<html>
	<head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /></head>
	<body>
		<strong>Difficulty level: <?= $result['difficulty'] ?></strong>
		<p><?= $result['text'] ?></p>

		<script src="//mandarinspot.com/static/mandarinspot.min.js" charset="UTF-8"></script>
		<script>mandarinspot.annotate();</script>
	</body>
</html>