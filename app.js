"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const child_process_1 = require("child_process");
const path_1 = __importDefault(require("path"));
const cors_1 = __importDefault(require("cors"));
const body_parser_1 = __importDefault(require("body-parser"));
const app = (0, express_1.default)();
app.use((0, cors_1.default)({
    origin: 'http://localhost:3000',
    credentials: true,
    methods: 'GET,POST',
    allowedHeaders: 'Content-Type, Authorization'
}));
app.use(body_parser_1.default.json());
// Static Files
app.use('/static', express_1.default.static(path_1.default.join(__dirname, 'frontend', 'build', 'static')));
app.use(express_1.default.static(path_1.default.join(__dirname, 'frontend', 'build')));
// Favicon Route
app.get('/favicon.ico', (req, res) => {
    res.sendFile(path_1.default.join(__dirname, 'frontend', 'build', 'favicon.ico'));
});
// Catch-all route for React App
app.get('*', (req, res) => {
    res.sendFile(path_1.default.join(__dirname, 'frontend/build', 'index.html'));
});
// API Route for K-Map Generation
app.post('/api/generate', async (req, res) => {
    const data = req.body;
    const numVars = data.variables.length;
    const rowSize = 2 ** Math.ceil(numVars / 2);
    const colSize = 2 ** Math.floor(numVars / 2);
    const grayCode = (n) => {
        if (n === 0)
            return [''];
        const firstHalf = grayCode(n - 1);
        const secondHalf = [...firstHalf].reverse();
        return firstHalf.map(code => '0' + code).concat(secondHalf.map(code => '1' + code));
    };
    const rowLabels = grayCode(Math.ceil(numVars / 2));
    const colLabels = grayCode(Math.floor(numVars / 2));
    let kmapMatrix = new Array(rowSize).fill(0).map(() => new Array(colSize).fill(0));
    data.minterms.forEach((minterm, idx) => {
        const row = Math.floor(idx / colSize);
        const col = idx % colSize;
        kmapMatrix[row][col] = minterm;
    });
    const flattenedMatrix = kmapMatrix.flat();
    let command = `python kmap.py ${numVars} ${data.variables.join('+')} ${rowLabels.join('+')} ${colLabels.join('+')} ${flattenedMatrix.join('+')}`;
    if (process.platform === 'win32') {
        command = `env\\Scripts\\activate.bat && ${command}`;
    }
    else {
        command = `source env/bin/activate && ${command}`;
    }
    (0, child_process_1.exec)(command, (error, stdout, stderr) => {
        if (error) {
            console.error(`exec error: ${error}`);
            return res.status(500).send(stderr);
        }
        return res.status(200).send('K-Map generated successfully.');
    });
});
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});