import React from 'react';

function RadioButtons({ onValueChange }: { onValueChange: (value: string) => void }) {
  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    // Call the callback function with the new value
    onValueChange(event.target.value);
  };

  return (
    <div>
      <input type="radio" value="sop" name="sopPos" onChange={handleChange} defaultChecked /> SOP
      <input type="radio" value="pos" name="sopPos" onChange={handleChange} /> POS
    </div>
  );
}

export default RadioButtons;
