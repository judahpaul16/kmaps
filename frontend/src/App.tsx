import React, { useState, useMemo } from 'react';
import { TextField, Button, Card, CardContent, Typography, Container, Box } from '@mui/material';
import './App.css';

function App() {
  const [variables, setVariables] = useState('');
  const [minterms, setMinterms] = useState('');
  const [image, setImage] = useState('');

  const numVars = useMemo(() => variables.split(' ').length, [variables]);
  const requiredMinterms = useMemo(() => Math.pow(2, numVars), [numVars]);

  const grayCode = (n: any): string[] => {
    if (n === 0) return [''];
    const firstHalf = grayCode(n - 1);
    const secondHalf = [...firstHalf].reverse();
    return firstHalf.map(code => '0' + code).concat(secondHalf.map(code => '1' + code));
  };

  const mintermLabels = useMemo(() => grayCode(numVars), [numVars]);

  const fetchImage = async () => {
    const mintermArray = minterms.split(' ').map(Number);
    if (mintermArray.length !== requiredMinterms) {
      alert(`Please enter exactly ${requiredMinterms} minterm values.`);
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ variables: variables.split(' '), minterms: mintermArray }),
      });
      if (response.ok) {
        const imageUrl = `http://localhost:8000/kmap.png?time=${new Date().getTime()}`;
        setImage(imageUrl);
      } else {
        console.error('Error fetching image');
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleVariablesChange = (e: any) => {
    setVariables(e.target.value);
    setMinterms(''); // Reset minterms if variables change
  };

  const handleMintermsChange = (e: any) => {
    setMinterms(e.target.value);
  };

  const handleSubmit = (e: any) => {
    e.preventDefault();
    fetchImage();
  };

  return (
    <Container maxWidth="sm" style={{ marginTop: '20px' }}>
      <Card>
        <CardContent>
          <Typography variant="h5" component="h2" gutterBottom>
            Karnaugh Map Generator
          </Typography>
          <form onSubmit={handleSubmit}>
            <TextField
              label="Variables (e.g. 'A B C D' or 'x y z')"
              variant="outlined"
              fullWidth
              margin="normal"
              value={variables}
              onChange={handleVariablesChange}
            />
            <Typography variant="subtitle1">
              Minterms: {mintermLabels.join(' ')}
            </Typography>
            <TextField
              label={`Enter ${requiredMinterms} minterm values`}
              variant="outlined"
              fullWidth
              margin="normal"
              value={minterms}
              onChange={handleMintermsChange}
            />
            <Button variant="contained" color="primary" type="submit" fullWidth style={{ marginTop: '10px' }}>
              Generate K-Map
            </Button>
          </form>
        </CardContent>
      </Card>
      {image && (
        <Box display="flex" justifyContent="center" marginTop="20px">
          <img src={image} alt="K-Map" style={{ maxWidth: '100%', height: 'auto' }} />
        </Box>
      )}
    </Container>
  );
}

export default App;
