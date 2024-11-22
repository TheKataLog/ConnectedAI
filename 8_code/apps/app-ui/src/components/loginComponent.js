import React, { useState } from 'react';

function LoginComponent({ onLogin, onGuestLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    try {
      e.preventDefault();
      await onLogin(username, password);
    } catch {
      setError('Invalid username or password.');
    }
  };

  const handleGuestLogin = async (e) => {
    try {
      e.preventDefault();
      await onGuestLogin();
    } catch {
      setError('Failed to login as Guest');
    }
  };

  return (
    <div style={styles.container}>
      <form style={styles.form} onSubmit={handleLogin}>
        <h2>Login</h2>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          style={styles.input}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={styles.input}
        />
        <button type="submit" style={styles.button}>
          Login
        </button>
        <p style={styles.error}>{error}</p>
        <p style={styles.guestLink} onClick={handleGuestLogin}>
          Continue as Guest
        </p>
      </form>
    </div>
  );
}

const styles = {
  body: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height: '100vh',
    margin: '0',
    fontFamily: "'Lato', sans-serif", // Matching font family
    background: 'linear-gradient(to bottom left, #79C7C5 40%, #F9FBFF 100%)', // Consistent gradient background
    color: '#777777', // Default text color
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    width: '300px',
    padding: '20px',
    boxShadow: '0 4px 8px rgba(119, 119, 119, 0.5)', // Updated shadow to match login screen
    backgroundColor: '#F9FBFF', // White color from login screen
    borderRadius: '8px',
    border: '1px solid #A1E2D9', // Secondary color for border
  },
  input: {
    margin: '10px 0',
    padding: '10px',
    fontSize: '16px',
    borderRadius: '4px',
    border: '1px solid #A1E2D9', // Secondary color for input border
    outline: 'none',
    transition: 'border-color 0.3s ease',
  },
  inputFocus: {
    borderColor: '#79C7C5', // Primary color for focus state
    boxShadow: '0 0 5px rgba(121, 199, 197, 0.5)', // Glow effect
  },
  button: {
    padding: '10px',
    fontSize: '16px',
    backgroundColor: '#467D7A', // Primary color for the button
    color: '#F9FBFF', // White color for text
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    transition: 'background-color 0.3s ease',
  },
  buttonHover: {
    backgroundColor: '#A1E2D9', // Secondary color for hover effect
  },
  guestLink: {
    marginTop: '15px',
    fontSize: '16px',
    color: '#467D7A', // Primary color for link
    textAlign: 'center',
    cursor: 'pointer',
    textDecoration: 'none',
  },
  guestLinkHover: {
    textDecoration: 'underline', // Underline on hover
  },
  error: {
    color: '#FF6B6B', // A contrasting red for error messages
  },
};

export default LoginComponent;
