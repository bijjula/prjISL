import React from 'react';
import VoiceToISL from './VoiceToISL';
import './App.css';

/**
 * Main App component for the Voice-to-ISL Translation System
 * 
 * This is the root component that renders the VoiceToISL component
 * providing the complete four-quadrant translation interface.
 */
function App(): JSX.Element {
  return (
    <div className="App">
      <VoiceToISL />
    </div>
  );
}

export default App;
