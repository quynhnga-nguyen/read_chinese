<?php
header('Access-Control-Allow-Origin: *');  

$pdo = new PDO('mysql:host=learn-chinese.cloudapp.net;port=3306;dbname=chinese_lang',
    'nga', 'Chinaman50100');
$pdo->exec("SET NAMES utf8");
$where_clause = "";
if (isset($_GET["difficulty"])) {
    $where_clause = " WHERE difficulty = " . $_GET["difficulty"];
}
$query = $pdo->prepare("SELECT text, difficulty FROM paragraph"
    . $where_clause . " ORDER BY RAND() LIMIT 1");
$query->execute();
$result = $query->fetch(PDO::FETCH_ASSOC);

$text = $result['text'];
$difficulty = $result['difficulty'];

$hv_query_stmt = "SELECT word, hanviet FROM frequency WHERE "
        . implode(" OR ",
            array_map(function($word) {
                global $pdo;
                return "word = " . $pdo->quote($word);
            }, preg_split('//u', $text, -1, PREG_SPLIT_NO_EMPTY)));
$query = $pdo->prepare($hv_query_stmt);
$query->execute();
$hv_map = array();
while ($row = $query->fetch(PDO::FETCH_ASSOC)) {
    $hv_map[$row['word']] = $row['hanviet'];
}
?>

<!DOCTYPE html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <title></title>
        <meta name="description" content="">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <link rel="icon" type="image/jpeg" href="han.jpg">
        <link rel="stylesheet" href="css/normalize.css">
        <link rel="stylesheet" href="css/main.css">
        <script src="js/vendor/modernizr-2.6.2.min.js"></script>
    </head>

    <body>
        <h1>Learn Chinese by sentences</h1>

        <div id="content">
            <strong>Difficulty level: <?= $difficulty ?></strong>
            <p><?= $text ?></p>

            <ul id="levels">
                <li><a href="?difficulty=1">Beginner</a></li>
                <li><a href="?difficulty=2">Intermediate</a></li>
                <li><a href="?difficulty=3">Advanced</a></li>
            </ul>
        </div>

        <script>
            var hvMap = <?= json_encode($hv_map) ?>;
        </script>

        <script src="//ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"></script>
        <script>window.jQuery || document.write('<script src="js/vendor/jquery-1.10.2.min.js"><\/script>')</script>
        <script src="js/plugins.js"></script>
        <script src="js/main.js"></script>

        <!-- Google Analytics: change UA-XXXXX-X to be your site's ID. -->
        <script>
            (function(b,o,i,l,e,r){b.GoogleAnalyticsObject=l;b[l]||(b[l]=
            function(){(b[l].q=b[l].q||[]).push(arguments)});b[l].l=+new Date;
            e=o.createElement(i);r=o.getElementsByTagName(i)[0];
            e.src='//www.google-analytics.com/analytics.js';
            r.parentNode.insertBefore(e,r)}(window,document,'script','ga'));
            ga('create','UA-XXXXX-X');ga('send','pageview');
        </script>

        <script src="//mandarinspot.com/static/mandarinspot.min.js" charset="UTF-8"></script>
        <script>mandarinspot.annotate();</script>
    </body>
</html>
