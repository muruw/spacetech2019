const {spawn, exec} = require('child_process');
const readline = require('readline');

//let arguments = ['-u', 'test.py', '1,2,3,4'];
let arguments = ['-u', 'simulation/main.py', '658988,6473296,660232,6474648'];
//658988, 6474648
//660232, 6473296

const subProcess = spawn('python', arguments, {
    cwd: '..'
});

//const subProcess = exec('python -u test.py 1,2,3,4');

const rl = readline.createInterface({
    input: subProcess.stdout
});

rl.on('line', (data) => {
    console.log(`line: ${data}`);
});

subProcess.stdout.on('data', (data) => {
    console.log(`stdout: ${data}`);
});

subProcess.stderr.on('data', (data) => {
    console.log(`stderr: ${data}`);
});

subProcess.on('close', (code) => {
    //rl.close();
    console.log(`child process exited with code ${code}`);
});