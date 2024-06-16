import { useState, useEffect } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import UploadReceipt from './components/UploadReceipt'

function App() {
  const [token, setToken] = useState('');

  useEffect(() => {
      const queryParams = new URLSearchParams(window.location.search);
      const token = queryParams.get('token');
      setToken(token);
  }, []);

  const VerifyToken = () => {
    const [token, setToken] = useState('');
    const [result, setResult] = useState(null);
  
    const handleSubmit = async (e) => {
      e.preventDefault();
      try {
        const response = await axios.post('http://127.0.0.1:5000/verify_token', { 
          headers: {
            'method': 'POST',
            'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token',
            'Access-Control-Allow-Origin': 'http://localhost:5000',
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${token}`,
            'mode': 'cors',
 
          }
         });
        setResult(response.data);
      } catch (error) {
        setResult(error);
      }
    };
  
    return (
      <div>
        <h2>Verify Token</h2>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            placeholder="Enter token"
            required
          />
          <button type="submit">Verify</button>
        </form>
        {result && (
          <div>
            <h3>Result:</h3>
            <pre>{JSON.stringify(result, null, 2)}</pre>
          </div>
        )}
      </div>
    );
  };

  return (
    <>
      <div className="App">
      <h1>Payment System</h1>
      {token ? <h2>Token: {token}</h2> : <h1>No Token</h1>}
      <UploadReceipt token={token}/>
      <VerifyToken />
    </div>
    </>
  )
}

export default App
