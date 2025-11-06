import { useState, useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'

import { login, createAccount, logout, authObserver } from './firebase.js'
import AuthForm from './AuthForm.jsx'
import Dashboard from './Dashboard.jsx';
import LoadingOverlay from './components/LoadingOverlay.jsx'

function App() {
    const [userInfo, setUserInfo] = useState(null);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(true);

    const signOut = async () => {
        setError('');
        await logout();
    }

    useEffect(() => authObserver(userInfo => {
        setUserInfo(userInfo);
        setLoading(false);
    }), []);

    return (
        <div className="min-h-screen flex items-center justify-center p-4 bg-indigo-900">
        <LoadingOverlay loading={loading}/>
        <Routes>
            <Route 
            path="/login"
            element={
                !userInfo ? <AuthForm loading={loading} setLoading={setLoading}
                                        error={error} setError={setError}
                            /> : <Navigate to="/dashboard"/>
            }
            />
            <Route 
            path="/dashboard"
            element={
                userInfo ? <Dashboard userInfo={userInfo} setLoading={setLoading}
                            /> : <Navigate to="/login"/>
            }
            />
            <Route 
            path="*"
            element={
                userInfo ? <Navigate to="/dashboard" /> : <Navigate to="/login" />
            }
            />
        </Routes>
        </div>
    );
}

export default App
    