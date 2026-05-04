import './App.css'
import { BrowserRouter, Routes, Router, Route } from 'react-router-dom'

import { Home } from './pages/Home/Home'

function AppContent() {
    return (
        <Routes>
            <Route path="/" element={<Home/>} />
            <Route path="/register" element={<Home/>} />
            <Route path="/login" element={<Home/>} />
            <Route path="/login-executor" element={<Home/>} />
            <Route path="/me" element={<Home/>} />
            <Route path="/news" element={<Home/>} />
            <Route path="/request" element={<Home/>} />
        </Routes>
    )
}

function App() {
  return (
    <>
        <BrowserRouter>
            <AppContent/>
        </BrowserRouter>
    </>
  )
}

export default App
