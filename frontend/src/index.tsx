import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

/**
 * React application entry point for Voice-to-ISL Translation System
 * 
 * This file bootstraps the React application and renders the main App component
 * into the DOM element with id 'root'.
 */

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
