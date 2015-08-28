<?php
$config_json = json_decode(file_get_contents("../config.json"), true);
$DB_CONN_STRING = $config_json["db_conn_string"];
$DB_USER_NAME = $config_json["db_user_name"];
$DB_PASSWORD = $config_json["db_password"];
?>