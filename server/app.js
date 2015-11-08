var express = require('express');
var exphbs = require('express-handlebars');
var mysql = require('mysql');
var nconf = require('nconf');
var bodyParser = require('body-parser');
var cookieParser = require('cookie-parser');

var easy = 50;
var intermediate = 75;

//
// Setup nconf to use (in-order):
//   1. Command-line arguments
//   2. Environment variables
//   3. The config.json file
//
nconf.argv().env().file({ file: __dirname + '/../config.json' });

var connection = mysql.createConnection({
	host: nconf.get('db_host'),
	user: nconf.get('db_user_name'),
	password: nconf.get('db_password'),
	database: nconf.get('db_name'),
});
var app = express();

app.engine('handlebars', exphbs({defaultLayout: 'main'}));
app.set('view engine', 'handlebars');

app.use(express.static('public'));
app.use(bodyParser.urlencoded({ extended: false }))
app.use(cookieParser());

app.get('/random', function (req, res) {
	var query, whereClause = '';
	if ("difficulty" in req.query) {
		switch (req.query.difficulty) {
			case "1":
				// Beginner
				whereClause = " AND avg_percentile < " + easy;
				break;
			case "2":
				// Intermediate
				whereClause = " AND avg_percentile < " + intermediate + " AND avg_percentile >= " + easy;
				break;
			case "3":
				// Advanced
				whereClause = " AND avg_percentile >= " + intermediate;
				break;
		}
	}

	query = 'SELECT id FROM paragraph'
	+ ', (SELECT RAND() * (SELECT MAX(id) FROM paragraph) AS tid) AS tmp'
	+ ' WHERE paragraph.id >= tmp.tid ' + whereClause + ' LIMIT 1;';

	connection.query(query, function (err, rows) {
		if (err) {
			console.log(err);
			return;
		}

		res.redirect('/paragraph?id=' + rows[0].id);
	});
});

app.get('/paragraph', function (req, res) {
	if ("id" in req.query) {
		query = 'SELECT text, avg_percentile FROM paragraph WHERE id = ' + req.query.id;

		connection.query(query, function (err, rows) {
			if (err) {
				console.log(err);
				return;
			}

			var text = rows[0].text;
			var percentile = parseFloat(rows[0].avg_percentile);
			var difficulty;

			if (percentile < easy) {
				difficulty = "Beginner";
			} else if (percentile < intermediate) {
				difficulty = "Intermediate";
			} else {
				difficulty = "Advanced";
			}
			difficulty += " (percentile = " + rows[0].avg_percentile + ")";

			res.cookie('last_id', req.query.id, { maxAge: 86400 });
			res.render('home', { text: text, difficulty: difficulty });
		});
	}
});

app.get('/', function (req, res) {
	if ("last_id" in req.cookies) {
		res.redirect('/paragraph?id=' + req.cookies.last_id);
	} else {
		res.redirect('/random');
	}
});

app.post('/hanviet', function (req, res) {
	var words = req.body.text;
	query = "SELECT word, hanviet FROM frequency WHERE "
		+ words.split('').map(function (word) { return "word = '" + word + "'"}).join(" OR ");
	var hvMap = {};
	connection.query(query, function (err, rows) {
		rows.forEach(function (row) {
			hvMap[row.word] = row.hanviet;
		});
		res.json(hvMap);
	});
})

var server = app.listen(3000);
