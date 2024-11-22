import React, { useState } from 'react';
import ChatComponent from './components/chatComponent';
import LoginComponent from './components/loginComponent';
import { login, getGuestToken } from './api/apiClient';
import robot from './assets/robotnew.png';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('token'));

  const handleLogin = async (username, password) => {
    const response = await login(username, password);
    localStorage.setItem('token', response.token);
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
  };

  const handleGuestLogin = async () => {
    try {
      const response = await getGuestToken();
      localStorage.setItem('token', response.token);
      setIsLoggedIn(true);
    } catch (error) {
      console.error('Guest login error:', error);
    }
  };

  return (
    <div style={styles.appContainer}>
      <header style={styles.header}>
        <div style={styles.robotImageContainer}>
          <img src={robot} alt="Logo" style={styles.robotImage} />
        </div>
        ShopWise Solutions
      </header>
      {isLoggedIn ? (
        <div style={styles.chatContainer}>
          <ChatComponent
            token={localStorage.getItem('token')}
            onLogout={handleLogout}
          />
        </div>
      ) : (
        <LoginComponent onLogin={handleLogin} onGuestLogin={handleGuestLogin} />
      )}
    </div>
  );
}

const styles = {
  appContainer: {
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    height: '100vh',
    backgroundColor:
      'linear-gradient(to bottom left, #79C7C5 40%, #F9FBFF 100%)', // Gradient from the login screen
    background: 'linear-gradient(to bottom left, #79C7C5 40%, #F9FBFF 100%)', // Consistent gradient background
    padding: '20px',
    boxSizing: 'border-box',
  },
  body: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height: '100vh',
    margin: '0',
    fontFamily: "'Lato', sans-serif", // Matching font family
    background: 'linear-gradient(to bottom left, #79C7C5 40%, #F9FBFF 100%)', // Consistent gradient background
    color: '#777777', // Default dark color for text
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center', // Center both text and logo
    fontSize: '2.5rem',
    fontWeight: 'bold',
    color: '#FFFFFF', // Primary color for text
    marginBottom: '20px',
    position: 'relative', // For layering effects
    textShadow: '2px 2px 4px rgba(0, 0, 0, 0.8)', // Add shadow for text visibility
    background:
      'linear-gradient(to bottom left, #467D7A 30%, #79C7C5 70%, #ADD8E6 100%)', // Darker teal with a tinge of blue
    borderRadius: '10px', // Smooth edges for the background
    padding: '10px 60px', // Add spacing around the text
    boxShadow: '0px 4px 8px rgba(0, 0, 0, 0.4)', // Add shadow for the header box
  },
  robotImageContainer: {
    position: 'relative',
    width: '80px',
    height: '80px',
    marginRight: '20px', // Add space between text and image
  },
  robotImage: {
    width: 'auto',
    height: '110%',
    position: 'relative',
    marginRight: '130px', // Add space between text and image
  },
  chatContainer: {
    width: '100%',
    maxWidth: '600px',
    height: '80vh',
    display: 'flex',
    flexDirection: 'column',
    backgroundColor: '#F9FBFF', // White shade from the login screen
    boxShadow: '0 4px 8px rgba(119, 119, 119, 0.5)', // Match shadow styling
    borderRadius: '8px',
    overflow: 'hidden',
    border: `1px solid #A1E2D9`, // Secondary color for border
  },
};

export default App;
