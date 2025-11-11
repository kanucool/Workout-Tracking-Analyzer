import { useState, useEffect } from 'react';

import UploadWorkoutForm from "./components/UploadWorkoutForm.jsx";
import LoadingOverlay from './components/LoadingOverlay.jsx';
import WorkoutAnalytics from './components/WorkoutAnalytics.jsx';

export default function Dashboard({ userInfo }) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [workoutData, setWorkoutData] = useState([]);

    const refresh = async () => {
        try {
            setLoading(true);
            setError('');

            if (!userInfo) {
                setWorkoutData([]);
                return;
            }

            const idToken = await userInfo.getIdToken();
            const response = await fetch(import.meta.env.VITE_BACKEND_API + "/workouts",
                {
                    "method": "GET",
                    "headers": {
                        "Authorization": `Bearer ${idToken}`,
                    }
                }
            );

            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || "Unknown Error - Try Again");

            setWorkoutData(data.workouts);
        }
        catch (err) {
            setError(err.message);
        }
        finally {
            setLoading(false);
        }
    };

    useEffect(() => {refresh()}, [userInfo]);

    return (
    <div className="w-full max-w-lg overflow-hidden relative bg-white">
        <LoadingOverlay loading={loading}/>
        <WorkoutAnalytics workoutData={workoutData}/>
        {/*
        <div className="flex flex-wrap max-w-lg gap-2">
            {workoutData.map((workout) => (
                <div key={`workout-date-${workout.date}`}>{workout.date},</div>
            ))}
        </div>
        */}
        {error}
        <UploadWorkoutForm userInfo={userInfo} setLoading={setLoading} />
        <button className="default-button" onClick={refresh}>Refresh</button>
    </div>
    );
}   