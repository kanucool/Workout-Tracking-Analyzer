import { Link } from 'react-router-dom'

export default function NavigationBar({ userInfo, logout, setLoading}) {
    return (
        <nav className="w-full bg-gray-100 text-indigo-800 p-4 shadow-md">
            <div className="flex gap-4 justify-self-end">
                <button onClick={async () => {setLoading(true); await logout(); setLoading(false)}}
                    className="default-button font-medium hover:bg-gray-300">
                    {!userInfo ? "Login" : "Sign out"}
                </button>
                <Link to="/dashboard" className="default-button font-medium hover:bg-gray-300">
                    Dashboard
                </Link>
            </div>
        </nav>
    );
}