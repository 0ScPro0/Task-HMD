import './App.css'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

import { Home } from './pages/Home/Home'
import { News } from './pages/News/News'
import { Login } from './pages/Login/Login'
import { Register } from './pages/Register/Register'
import { LoginExecutor } from './pages/LoginExecutor/LoginExecutor'
import { Me } from './pages/Me/Me'
import { Request } from './pages/Request/Request'

import { useAuthInit } from './hooks/useAuth'

function AppContent() {
    useAuthInit();
    return (
        <Routes>
            <Route path="/" element={<Home/>} />
            <Route path="/register" element={<Register/>} />
            <Route path="/login" element={<Login/>} />
            <Route path="/login-executor" element={<LoginExecutor/>} />
            <Route path="/me" element={<Me/>} />
            <Route path="/news" element={<News/>} />
            <Route path="/request" element={<Request/>} />
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
