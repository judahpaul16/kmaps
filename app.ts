import express, { Request, Response } from 'express';
import { exec } from 'child_process';
import path from 'path';
import cors from 'cors';
import bodyParser from 'body-parser';

type KMapData = {
    variables: string[];
    minterms: number[];
};

const app = express();

app.use(cors({
  origin: '*',
  credentials: true,
  methods: 'GET,POST',
  allowedHeaders: 'Content-Type, Authorization',
  // Add the following line to set the CSP
  exposedHeaders: 'Content-Security-Policy',
  preflightContinue: false,
  optionsSuccessStatus: 204
}));

// Set Content Security Policy
app.use((req, res, next) => {
  res.setHeader("Content-Security-Policy", "default-src 'self'; img-src 'self' data:; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';");
  next();
});

app.use(bodyParser.json());

// Static Files
app.use('/static/*', express.static(path.join(__dirname, 'frontend', 'build', 'static')));
app.use('/static/css/*', express.static(path.join(__dirname, 'frontend', 'build', 'static', 'css')));
app.use('/static/js/*', express.static(path.join(__dirname, 'frontend', 'build', 'static', 'js')));
app.use(express.static(path.join(__dirname, 'frontend', 'build')));

// Favicon Route
app.get('/favicon.ico', (req: Request, res: Response) => {
  res.sendFile(path.join(__dirname, 'frontend', 'build', 'favicon.ico'));
});

// React App
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'frontend/build', 'index.html'));
});

// API Route for K-Map Generation
app.post('/api/generate', async (req: Request, res: Response) => {
    const data = req.body as KMapData;
  
    const numVars = data.variables.length;
    const rowSize = 2 ** Math.ceil(numVars / 2);
    const colSize = 2 ** Math.floor(numVars / 2);
  
    const grayCode = (n: number): string[] => {
      if (n === 0) return [''];
      const firstHalf = grayCode(n - 1);
      const secondHalf = [...firstHalf].reverse();
      return firstHalf.map(code => '0' + code).concat(secondHalf.map(code => '1' + code));
    };
  
    const rowLabels = grayCode(Math.ceil(numVars / 2));
    const colLabels = grayCode(Math.floor(numVars / 2));
  
    let kmapMatrix: number[][] = new Array(rowSize).fill(0).map(() => new Array(colSize).fill(0));
    data.minterms.forEach((minterm, idx) => {
      const row = Math.floor(idx / colSize);
      const col = idx % colSize;
      kmapMatrix[row][col] = minterm;
    });
  
    const flattenedMatrix = kmapMatrix.flat();

    let command = `python kmap.py ${numVars} ${data.variables.join('+')} ${rowLabels.join('+')} ${colLabels.join('+')} ${flattenedMatrix.join('+')}`;
    if (process.platform === 'win32') {
        command = `env\\Scripts\\activate.bat && ${command}`;
    } else {
        command = `source env/bin/activate && ${command}`;
    }

    exec(command, (error, stdout, stderr) => {
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
