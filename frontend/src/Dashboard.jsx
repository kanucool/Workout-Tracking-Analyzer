import UploadWorkoutForm from "./UploadWorkoutForm.jsx";

export default function Dashboard({ userInfo, setLoading }) {
    return (<UploadWorkoutForm userInfo={userInfo} setLoading={setLoading} />);
}