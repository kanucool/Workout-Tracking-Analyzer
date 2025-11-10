import { useState } from 'react';

import UploadWorkoutForm from "./UploadWorkoutForm.jsx";
import LoadingOverlay from './components/LoadingOverlay.jsx';

export default function Dashboard({ userInfo }) {
    const [loading, setLoading] = useState(false);
    return (
    <div className="w-full max-w-lg overflow-hidden relative">
        <LoadingOverlay loading={loading}/>
        <UploadWorkoutForm userInfo={userInfo} setLoading={setLoading} />
    </div>
    );
}   