const http = require('http');
const express = require('express');
const {spawn, exec} = require('child_process');
const WebSocket = require('ws');
const readline = require('readline');
const crypto = require("crypto");

const port = 8088;

let subProcesses = {};

const app = express();

app.use(express.static('../web'));

const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

wss.on('connection', (ws) => {
    ws.uuid = crypto.randomBytes(16).toString("hex");

    console.log('socket connected', ws.uuid);

    ws.on('message', (message) => {
        console.log('received: %s', message);

        try {
            const request = JSON.parse(message.toString('utf8'));

            console.log('request', request);

            if (request.type === 'get-positions') {
                getPositionsWithUpdates(ws.uuid, request.bbox, request.existing, (positions) => {
                    console.log('onUpdate', positions);
                    ws.send(JSON.stringify({type: 'positions', positions}));
                }, () => {
                    console.log('onDone');
                    ws.send(JSON.stringify({type: 'positions-done'}));
                });
            } else if (request.type === 'stop') {
                killSubProcess(ws.uuid);
            }
        } catch (e) {
            console.error(e);
        }
    });

    ws.on('close', (code, reason) => {
        console.log('socket closed', code, reason);
        killSubProcess(ws.uuid);
    });
});

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

function killSubProcess(uuid) {
    if (subProcesses[uuid]) {
        console.log('killSubProcess', uuid);
        subProcesses[uuid].kill();
    }

    delete subProcesses[uuid];
}

function getPositionsWithUpdates(uuid, bbox, existingAntennas, onUpdate, onDone) {
    console.log('getPositionsWithUpdates', bbox, existingAntennas);

    let arguments = ['-u', 'simulation/main.py', bbox];

    if (existingAntennas) {
        arguments.push(existingAntennas);
    }

    killSubProcess(uuid);

    const subProcess = spawn('python', arguments, {
        cwd: '..'
    });

    subProcesses[uuid] = subProcess;

    const rl = readline.createInterface({
        input: subProcess.stdout
    });

    rl.on('line', (data) => {
        console.log(`line: ${data}`);

        const boundsArray = bbox.split(',').map(stringValue => parseFloat(stringValue));

        try {
            const positions = JSON.parse(data).map(position => processorToWorldObject(position, boundsArray));

            onUpdate(positions);
        } catch(e) {
            console.error(e);
        }
    });

    subProcess.stdout.on('data', (data) => {
        console.log(`stdout: ${data}`);
    });

    subProcess.stderr.on('data', (data) => {
        console.log(`stderr: ${data}`);
    });

    subProcess.on('close', (code) => {
        rl.close();
        console.log(`child process exited with code ${code}`);
        onDone();
    });
}

function processorToWorldObject(normalizedObject, worldAreaBounds) {
    console.log('processorToWorldObject', normalizedObject, worldAreaBounds);
    let {x, y, ...worldObject} = normalizedObject;
    const [x1, y1, x2, y2] = worldAreaBounds;

    console.log(x, y, x1, y1, x2, y2);

    worldObject.x = x1 + x * (x2 - x1);
    worldObject.y = y1 + y * (y2 - y1);

    return worldObject;
}

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

server.listen(port);

