import { useState } from 'react'

import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword } from "firebase/auth";
import { initializeApp } from "firebase/app";
import { getFirestore } from 'firebase/firestore/lite';

const firebaseConfig = {
  apiKey: "AIzaSyBf-0A7f3zIsjg7LV1YchzcWSM9icEqtuE",
  authDomain: "workout-analyzer-4834d.firebaseapp.com",
  projectId: "workout-analyzer-4834d",
  storageBucket: "workout-analyzer-4834d.firebasestorage.app",
  messagingSenderId: "617494723125",
  appId: "1:617494723125:web:86251b421e4a37a39a8f7c",
  measurementId: "G-JRK6ZQ5Q6F"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

const createAccount = async(email, password) => await createUserWithEmailAndPassword(auth, email, password);
const login = async(email, password) => await signInWithEmailAndPassword(auth, email, password);

function App() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [idToken, setIdToken] = useState('');
    const [userInfo, setUserInfo] = useState('');
    const [error, setError] = useState('');

    const signIn = async() => {
        setIdToken('');
        setError('');

        try {setIdToken(await ((await login(email, password)).user.getIdToken()));}
        catch (err) {setError(err.message);}
    }

    const signUp = async() => {
        setIdToken('');
        setError('');

        try {
            setIdToken((await createAccount(email, password)).user.getIdToken());
            alert('You have successfully signed up!');
        }
        catch (err) {setError(err.message);}
    }

    const authorize = async() => {
        setError('');
        setUserInfo('Loading...');

        fetch('http://localhost:8000/auth/me', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${idToken}`
            }
        }).then(response => {
            return response.json().then(data => {
                if (!response.ok) throw new Error(data.detail || 'Request failed');
                return data;
            });
        }).then(data => {
            setUserInfo(JSON.stringify(data, null, 2));
        }).catch(err => {
            setError(err.message);
            setUserInfo('');
        });
    }

    return (
        <div>
            <h1>Workout Analyzer LOGIN</h1>
            <div>
                <label>
                Email:
                <input type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                />
                </label>
                <br></br>
                <label>
                Password 
                <input type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />
                </label>
                <br></br>
                <button onClick={signUp}>Sign Up</button>
                <button onClick={signIn}>Sign In</button>
                <br></br>
                <button onClick={authorize}>Authorize</button>
            </div>

            {error && <pre style={{ color: 'red', marginTop: '10px' }}>Error: {error}</pre>}

            <p>{idToken || 'Not logged in'}</p>
            <p>{userInfo}</p>
        </div>
    )
}

export default App
