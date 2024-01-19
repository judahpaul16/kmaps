import React, { useState, useMemo, useEffect } from 'react';
import { TextField, Button, Card, CardContent, Typography, Container, Box } from '@mui/material';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSpinner } from '@fortawesome/free-solid-svg-icons';
import './App.css';

interface AppProps {}

const App: React.FC<AppProps> = () => {
  const [variables, setVariables] = useState<string>('');
  const [minterms, setMinterms] = useState<string>('');
  const [image, setImage] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const numVars = useMemo(() => variables.split(' ').length, [variables]);
  const requiredMinterms = useMemo(() => Math.pow(2, numVars), [numVars]);

  const grayCode = (n: number): string[] => {
    if (n === 0) return [''];
    const firstHalf = grayCode(n - 1);
    const secondHalf = [...firstHalf].reverse();
    return firstHalf.map(code => '0' + code).concat(secondHalf.map(code => '1' + code));
  };

  const mintermLabels = useMemo(() => grayCode(numVars), [numVars]);

  const fetchImage = async (orderedMinterms: number[]) => {
    setIsLoading(true);
  
    // Use ordered minterms instead of splitting the minterms state
    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ variables: variables.split(' '), minterms: orderedMinterms }),
      });
      if (response.ok) {
        const imageUrl = `/kmap.png?time=${new Date().getTime()}`;
        setImage(imageUrl);
      } else {
        console.error('Error fetching image');
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleVariablesChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setVariables(event.target.value);
    setMinterms('');
  };

  // Helper function to convert a binary number to its Gray code equivalent
  const binaryToGray = (binary: string): string => {
    const binaryNum = parseInt(binary, 2);
    const grayNum = binaryNum ^ (binaryNum >> 1);
    return grayNum.toString(2).padStart(binary.length, '0');
  };

  // Function to create a mapping from binary to Gray code
  const createBinaryToGrayMapping = (grayLabels: string[]): Record<string, number> => {
    return grayLabels.reduce((map: Record<string, number>, grayLabel: string, index: number) => {
      const binaryLabel = index.toString(2).padStart(grayLabel.length, '0');
      const grayCode = binaryToGray(binaryLabel);
      map[grayCode] = index;
      return map;
    }, {});
  };

  // Function to reorder minterms to match the Gray code sequence
  function orderMintermsToGrayCode(minterms: number[], grayLabels: string[]): number[] {
    const binaryToGrayMap = createBinaryToGrayMapping(grayLabels);
    const orderedMinterms = new Array(minterms.length);
    
    minterms.forEach((mintermValue: number, index: number) => {
      const binaryIndex = index.toString(2).padStart(grayLabels.length, '0');
      const grayIndex = binaryToGrayMap[binaryIndex];
      orderedMinterms[grayIndex] = mintermValue;
    });

    return orderedMinterms;
  }

  // When setting the minterms, ensure they match the Gray code order
  const handleMintermsChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setMinterms(event.target.value);
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
  
    // Split the minterms and convert them to numbers
    const inputMinterms = minterms.split(' ').filter(minterm => minterm !== '').map(Number);
  
    // Check if the number of minterms is correct and all are numbers
    if (inputMinterms.length !== requiredMinterms || inputMinterms.some(isNaN)) {
      alert(`Please enter exactly ${requiredMinterms} numeric minterm values.`);
      return;
    }
  
    fetchImage(inputMinterms);
  };  

  // Function to determine the highlighted index
  const highlightedIndex = () => {
    const mintermArray = minterms.trim().split(' ').filter(Boolean);
    return mintermArray.length - 1;
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
            <Typography variant="subtitle1" gutterBottom>
              Minterms:&nbsp;
              {mintermLabels.map((label, index) => (
                <span
                  key={index}
                  className={index === highlightedIndex() ? 'highlighted' : ''}
                  style={{ marginRight: '5px' }}
                >
                  {label}
                </span>
              ))}
            </Typography>
            <TextField
              label={`Enter ${requiredMinterms} minterm values`}
              variant="outlined"
              fullWidth
              margin="normal"
              value={minterms}
              onChange={handleMintermsChange}
            />
            <Button variant="contained" color="primary" type="submit" fullWidth style={{ marginTop: '10px' }} disabled={isLoading}>
              {isLoading ? <FontAwesomeIcon icon={faSpinner} spin /> : 'Generate K-Map'}
            </Button>
          </form>
        </CardContent>
      </Card>
      {image && (
        <Box display="flex" justifyContent="center" marginTop="20px">
          <img key={image} src={image} alt="K-Map" style={{ maxWidth: '100%', height: 'auto' }} />
        </Box>
      )}
    </Container>
  );
}

export default App;