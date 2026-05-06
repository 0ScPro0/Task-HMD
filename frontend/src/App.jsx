import './App.css'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

import { Home } from './pages/Home/Home'
import { News } from './pages/News/News'
import { Login } from './pages/Login/Login'
import { Register } from './pages/Register/Register'
import { Me } from './pages/Me/Me'
import { Request } from './pages/Request/Request'
import { AdminRedirect } from './pages/AdminRedirect/AdminRedirect'

import { AuthLoader } from './components/auth/AuthLoader/AuthLoader'
import { ProtectedRoute } from './components/auth/ProtectedRoute/ProtectedRoute'

function AppContent() {
    return (
        <AuthLoader>
            <Routes>
                <Route path="/" element={<Home/>} />
                <Route path="/register" element={<Register/>} />
                <Route path="/login" element={<Login/>} />
                <Route path="/admin" element={
                    <ProtectedRoute>
                        <AdminRedirect/>
                    </ProtectedRoute>
                } />
                <Route path="/me" element={
                    <ProtectedRoute>
                        <Me/>
                    </ProtectedRoute>
                } />
                <Route path="/news" element={
                    <ProtectedRoute>
                        <News/>
                    </ProtectedRoute>
                } />
                <Route path="/request" element={
                    <ProtectedRoute>
                        <Request/>
                    </ProtectedRoute>
                } />
            </Routes>
        </AuthLoader>
    )
}

function App() {
    return (
        <BrowserRouter>
            <AppContent/>
        </BrowserRouter>
    )
}

export default App