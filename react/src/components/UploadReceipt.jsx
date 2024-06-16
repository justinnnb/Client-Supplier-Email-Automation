import React, { useState } from 'react';
import axios from 'axios';

const UploadReceipt = (token) => {
  const [file, setFile] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('file', file);
    formData.append('token', token.token);

    try {
      // const response = await axios.post(`${import.meta.env.VITE_API_URL}/upload_payment`, formData, {

      const response = await axios.post(`http://127.0.0.1:5010/api/upload_payment`, formData, {
        headers: {
          // 'method': 'POST',
          // 'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token',
          // 'Access-Control-Allow-Origin': 'http://127.0.0.1:5173/',
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${token.token}`,
          // 'mode': 'cors',
          
        }
      }); 
      console.log('File uploaded successfully:', response.data);
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  return (
    <div>
      <h2>Upload Receipt</h2>
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={handleFileChange} required />
        <button type="submit">Upload</button>
      </form>
    </div>
  );
};

export default UploadReceipt;
