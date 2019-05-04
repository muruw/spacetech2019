const express = require('express');
const app = express();
const exec = require('child_process').exec;

const port = 8088;

app.use(express.static('../web'));

const positions = [[659782.0000000091, 6473717.999999775]];

app.get('/get-positions', (req, res) => {
    const bboxPattern = /[-.\d]+,[-.\d]+,[-.\d]+,[-.\d]+/;

    console.log('get-positions', req.query);

    if (typeof req.query.bbox !== 'string') {
        res.status(400);
        res.send('bbox undefined');
        return;
    }

    const match = bboxPattern.exec(bboxPattern);

    if (Array.isArray(match) && match.length === 1) {
        res.status(400);
        res.send('Invalid bbox format');
        return;
    }

    getPositions(req.query.bbox, (error, result) => {
        if (error) {
            res.status(400);
            res.send('Failed');
            return;
        }

        res.json(result);
    })
});

function getPositions(bbox, callback) {
    exec('python test.py ' + bbox, (error, stdout, stderr) => {
        if (error) {
            console.error(error);
            callback('Failed');
            return;
        }

        if (stderr) {
            console.error(stderr);
            callback('Failed');
            return;
        }

        console.log(stdout);

        try {
            callback(null, JSON.parse(stdout));
        } catch(e) {
            console.error(e);
            callback('Failed');
        }
    });
}

app.listen(port);

