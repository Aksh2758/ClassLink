import React, { useEffect, useState } from 'react';
import { useParams } from "react-router-dom";
import axios from 'axios';

const CircularDetails = () => {
    const { circular_id } = useParams();
    const [circular, setCircular] = useState(null);
    const [error, setError] = useState('');

    const API_BASE_URL = "http://localhost:5000/api/circulars";

    useEffect(() => {
        const fetchCircular = async () => {
            try {
                const token = localStorage.getItem("token");
                const res = await axios.get(`${API_BASE_URL}/${circular_id}`, {
                    headers: { Authorization: `Bearer ${token}` }
                });

                if (res.data.success) {
                    setCircular(res.data.circular);
                } else {
                    setError("Circular not found");
                }
            } catch (err) {
                setError("Error loading circular");
            }
        };

        fetchCircular();
    }, [circular_id]);

    if (error) return <h2>{error}</h2>;
    if (!circular) return <h2>Loading...</h2>;

    return (
        <div style={{ padding: "20px" }}>
            <h1>{circular.title}</h1>
            <p>{circular.content}</p>
            
            {circular.attachment_url && (
                <a 
                    href={`http://localhost:5000${circular.attachment_url}`} 
                    target="_blank" 
                    rel="noopener noreferrer"
                >
                    View Attachment
                </a>
            )}
        </div>
    );
};

export default CircularDetails;
