const express = require('express');
const app = express();
const exec = require('child_process').exec;

const port = 8088;

app.use(express.static('../web'));

const positions = [[659782.0000000091, 6473717.999999775]];

app.get('/get-positions', (req, res) => {
    const bboxPattern = /[-.\d]+,[-.\d]+,[-.\d]+,[-.\d]+/;
    const existingAntennaPattern = /([-.\d]+,[-.\d]+,\w+,?)+/;

    console.log('get-positions', req.query);

    if (typeof req.query.bbox !== 'string') {
        res.status(400);
        res.send('Parameter bbox undefined');
        return;
    }

    const match = bboxPattern.exec(req.query.bbox);

    if (!Array.isArray(match) || match.length !== 1) {
        res.status(400);
        res.send('Invalid format for parameter bbox');
        return;
    }

    if (typeof req.query.existing === 'string' && req.query.existing.length > 0) {
        const match = existingAntennaPattern.exec(req.query.existing);

        if (!Array.isArray(match)) {
            res.status(400);
            res.send('Invalid format for parameter existing');
            return;
        }
    }

    getPositions(req.query.bbox, req.query.existing, (error, result) => {
        if (error) {
            res.status(400);
            res.send('Failed');
            return;
        }

        res.json(result);
    })
});

function getPositions(bbox, existingAntennas, callback) {
    let command = 'python test.py ' + bbox;

    if (existingAntennas) {
        command += ' ' + existingAntennas;
    }

    exec(command, (error, stdout, stderr) => {
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

