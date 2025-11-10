import { useState } from 'react';

import LoadingOverlay from './components/LoadingOverlay.jsx';

export default function UploadWorkoutForm({ userInfo }) {
    const [fileList, setFileList] = useState([]);
    const [uploadRes, setUploadRes] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const fileListChange = (e) => {
        e.preventDefault();
        if (e.target.files) {
            setFileList(Array.from(e.target.files));
            setUploadRes([]);
        }
    }

    const uploadFileList = async (e) => {
        e.preventDefault();
        setError('');

        if (!fileList.length) {
            setError("Select one or more files before uploading.");
            return;
        }

        setUploadRes([]);

        try {
            setLoading(true);
            const idToken = await userInfo.getIdToken();

            const uploadFile = async (file) => {
                const formData = new FormData();
                formData.append("workout_log_file", file);

                const response = await fetch(import.meta.env.VITE_BACKEND_UPLOAD_API_ENDPOINT,
                    {
                        "method": "POST",
                        "headers": {
                            "Authorization": `Bearer ${idToken}`,
                        },
                        "body": formData,
                    }
                );

                const data = await response.json();
                if (!response.ok) throw new Error(data.detail || `Upload failed for ${file.name}`);
            }
            
            const uploadPromises = fileList.map((file) => uploadFile(file));
            const uploadResults = await Promise.allSettled(uploadPromises);

            const newUploadRes = uploadResults.map((res, idx) => `${fileList[idx].name}: ${res.status == "fulfilled" ? "Uploaded" : res.reason.message}`);
            setUploadRes(newUploadRes);
            setFileList([]);
        }
        catch (err) {
            setError(err.message);
        }
        finally {
            setLoading(false);
        }
    }

    return (
        <div className="relative bg-white rounded-lg shadow-xl p-8">
            <LoadingOverlay loading={loading}/>
            <form className="space-y-4" onSubmit={uploadFileList}>
                <h2 className="text-2xl font-bold text-center text-gray-800">
                    Upload Workouts
                </h2>
                <div>
                    <label htmlFor="file-select" className="block text-sm font-medium text-gray-700">
                        Select Files
                    </label>    
                    <input
                        id="file-select" type="file" accept=".txt,.pdf" onChange={(e) => fileListChange(e)} onClick={(e) => e.target.value = null} multiple
                        className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 hover:file:cursor-pointer"
                    />
                </div>
                
                {fileList.length > 0 && (
                    <div>
                        <div className="text-sm text-gray-600">
                            <ul className="list-disc list-inside">
                                {fileList.map((file, index) => (
                                    <li key={`file-list-${index}`}>{file.name}</li>
                                ))}
                            </ul>
                        </div>
                    </div>)}

                <div className="flex gap-4 pt-2">
                    <button 
                        type="submit"
                        className={"bg-indigo-500 focus:ring-indigo-800 hover:bg-indigo-600 text-white default-button"}
                    >
                        Upload
                    </button>
                </div>
                {uploadRes.length > 0 && (
                    <div className="text-sm text-gray-600">
                        <ul className="list-disc list-inside">
                                {uploadRes.map((res, index) => (
                                    <li key={`upload-res-${index}`}
                                        className={res.split(": ").pop() == "Uploaded"
                                                ? "text-green-500" : "text-red-600"}
                                    >{res}</li>
                                ))}
                            </ul>
                    </div>
                )}
                {error && <div>{error}</div>}
            </form>
        </div>
    );
}