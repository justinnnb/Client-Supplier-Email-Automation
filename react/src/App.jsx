import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import UploadReceipt from './components/UploadReceipt'

function App() {

  return (
    <>
      <div className="App">
      <h1>Payment System</h1>
      <UploadReceipt />
    </div>
    </>
  )
}

export default App
