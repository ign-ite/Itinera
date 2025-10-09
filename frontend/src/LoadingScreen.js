import React, { useState, useEffect } from 'react';

function LoadingScreen({ onComplete }) {
  const [progress, setProgress] = useState(0);
  const [backendStatus, setBackendStatus] = useState('checking');

  useEffect(() => {
    const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    
    // Ping backend to wake it up
    const pingBackend = async () => {
      try {
        const startTime = Date.now();
        const response = await fetch(`${API_URL}/`, {
          method: 'GET',
          headers: { 'Accept': 'application/json' }
        });
        
        const endTime = Date.now();
        const responseTime = endTime - startTime;
        
        if (response.ok) {
          setBackendStatus('ready');
          console.log(`Backend ready in ${responseTime}ms`);
        } else {
          setBackendStatus('error');
        }
      } catch (error) {
        console.error('Backend ping failed:', error);
        setBackendStatus('error');
      }
    };

    pingBackend();

    // Progress bar animation
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(progressInterval);
          return 100;
        }
        // Slow down near the end to wait for backend
        if (prev >= 90 && backendStatus !== 'ready') {
          return prev + 0.5;
        }
        return prev + 2;
      });
    }, 50);

    return () => clearInterval(progressInterval);
  }, [backendStatus]);

  useEffect(() => {
    if (progress >= 100 && backendStatus === 'ready') {
      setTimeout(onComplete, 300);
    }
  }, [progress, backendStatus, onComplete]);

  return (
    <div className="fixed inset-0 bg-white flex flex-col items-center justify-center z-50">
      {/* Logo */}
      <div className="mb-8">
        <img 
          src="/logo192.png" 
          alt="Itinera" 
          className="w-24 h-24 animate-pulse"
        />
      </div>

      {/* Brand Name */}
      <h1 className="text-4xl font-bold mb-2">
        <span className="text-blue-600">Itin</span>
        <span className="text-gray-800">era</span>
      </h1>
      <p className="text-gray-600 mb-8">AI Travel Planner</p>

      {/* Progress Bar */}
      <div className="w-64 h-1 bg-gray-200 rounded-full overflow-hidden mb-4">
        <div 
          className="h-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all duration-300 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Status Text */}
      <p className="text-sm text-gray-500">
        {backendStatus === 'checking' && 'Connecting to server...'}
        {backendStatus === 'ready' && 'Ready to plan your journey'}
        {backendStatus === 'error' && 'Server unavailable (may take 60s to wake)'}
      </p>

      {/* Loading Dots Animation */}
      <div className="flex gap-1 mt-4">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"
            style={{ animationDelay: `${i * 0.15}s` }}
          />
        ))}
      </div>
    </div>
  );
}

export default LoadingScreen;