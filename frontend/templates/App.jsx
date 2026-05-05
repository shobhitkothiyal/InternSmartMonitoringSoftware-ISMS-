import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './Login';
import Admin from './Admin';
import SuperAdmin from './SuperAdmin';
import SubAdmin from './SubAdmin';
import Dashboard from './Dashboard';
import { getApiUrl } from './config';

const ProtectedRoute = ({ children }) => {
    const [sessionState, setSessionState] = useState('checking');

    useEffect(() => {
        let isMounted = true;

        fetch(getApiUrl('/api/session'), { credentials: 'include' })
            .then((response) => {
                if (!isMounted) return;
                setSessionState(response.ok ? 'authenticated' : 'unauthenticated');
            })
            .catch(() => {
                if (!isMounted) return;
                setSessionState('unauthenticated');
            });

        return () => {
            isMounted = false;
        };
    }, []);

    if (sessionState === 'checking') {
        return (
            <div className="min-h-screen flex items-center justify-center bg-slate-50 text-slate-600 font-semibold">
                Checking session...
            </div>
        );
    }

    if (sessionState === 'unauthenticated') {
        localStorage.removeItem('currentUser');
        localStorage.removeItem('token');
        return <Navigate to="/" replace />;
    }

    return children;
};

const App = () => {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Login />} />
                <Route path="/admin/*" element={<ProtectedRoute><Admin /></ProtectedRoute>} />
                <Route path="/superadmin/*" element={<ProtectedRoute><SuperAdmin /></ProtectedRoute>} />
                <Route path="/mentor/*" element={<ProtectedRoute><SubAdmin /></ProtectedRoute>} />
                <Route path="/dashboard" element={<Dashboard user="User" />} />
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </Router>
    );
};

export default App;
