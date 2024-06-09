import React, { useState } from 'react';
import axios from 'axios';

const UploadReceipt = () => {
  const [file, setFile] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('file', file);
    formData.append('student_name', 'John Doe'); // Replace with actual data
    formData.append('folder_id', 'your_google_drive_folder_id'); // Replace with actual folder ID

    try {
      const response = await axios.post(`${import.meta.env.VITE_API_URL}/api/upload-screenshot`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${import.meta.env.VITE_API_KEY}`
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
