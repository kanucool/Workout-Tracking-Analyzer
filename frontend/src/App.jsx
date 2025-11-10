import { useState, useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'

import { logout, authObserver } from './firebase.js'
import AuthForm from './AuthForm.jsx'
import Dashboard from './Dashboard.jsx';
import NavigationBar from './components/NavigationBar.jsx';
import LoadingOverlay from './components/LoadingOverlay.jsx';

function App() {
    const [userInfo, setUserInfo] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    const signOut = async () => {
        setError('');
        await logout();
    }

    useEffect(() => authObserver(userInfo => {
        setUserInfo(userInfo);
        setLoading(false);
    }), []);

    return (
        <div className="min-h-screen flex flex-col bg-gray-100">
            <LoadingOverlay loading={loading}/>
            <NavigationBar userInfo={userInfo} logout={signOut} setLoading={setLoading}/>

            <div className="flex grow items-center justify-center p-4
                             bg-indigo-950 bg-[url('public/grit.png')]">
            <Routes>
                <Route 
                path="/login"
                element={
                    !userInfo ? <AuthForm/> : <Navigate to="/dashboard"/>
                }
                />
                <Route 
                path="/dashboard"
                element={
                    userInfo ? <Dashboard userInfo={userInfo}/>: 
                                                            <Navigate to="/login"/>
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
        </div>
    );
}

export default App
    