import { useState } from 'react'
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
  console.log('test')

  return (
    <>
      <div className="App">
      <h1>Payment System</h1>
      {token ? <h2>Token: {token}</h2> : <h1>No Token</h1>}
      <UploadReceipt />
    </div>
    </>
  )
}

export default App
