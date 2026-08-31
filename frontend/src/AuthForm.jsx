import { useState } from 'react';
import {login, createAccount } from './firebase.js'
import LoadingOverlay from './components/LoadingOverlay.jsx';

export default function AuthForm() {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const signIn = async (e) => {
            setError('');
            e.preventDefault();
            try {
                setLoading(true);
                await login(email, password);
            }
            catch (err) {setError(err.message);}
            finally {setLoading(false);}
        }
    
    const signUp = async (e) => {
        e.preventDefault();
        setError('');
        try {
            setLoading(true);
            await createAccount(email, password);
        }
        catch (err) {setError(err.message);}
        finally {setLoading(false);}
    }

    return (
        <div className="relative w-full max-w-lg bg-white rounded-lg shadow-xl p-8">
            <LoadingOverlay loading={loading}/>
            <form className="space-y-4" onSubmit={signIn}>
                <h2 className="text-2xl font-bold text-center text-gray-800">
                    Workout Analyzer Login
                </h2>

                <div>
                    <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                        Email
                    </label>
                    <input
                        id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                </div>
                <div>
                    <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                        Password
                    </label>
                    <input
                        id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                </div>
                <fieldset disabled={loading}>
                    <div className="flex gap-4 pt-2">
                            <button 
                                type="submit"
                                className={"bg-indigo-500 focus:ring-indigo-800 hover:bg-indigo-600 text-white default-button"}
                            >
                                Login
                            </button>
                            <button 
                                type="button" 
                                onClick={signUp} 
                                className={"bg-gray-200 focus:ring-gray-400 hover:bg-gray-300 text-gray-800 default-button"}
                            >
                                Sign Up
                            </button>
                    </div>
                </fieldset>
                {error && <div>{error}</div>}
            </form>
        </div>
    );
}