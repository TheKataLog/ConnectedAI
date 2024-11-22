export const BASE_URL = 'https://shopwise-api-server-kgf5ffrboa-ts.a.run.app'; //http://localhost:5001';

export async function login(username, password) {
  const response = await fetch(`${BASE_URL}/api/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!response.ok) throw new Error('Login failed');
  return response.json();
}

export async function getGuestToken() {
  const response = await fetch(`${BASE_URL}/api/getGuestToken`);
  if (!response.ok) throw new Error('Guest login failed');
  return response.json();
}

export async function sendMessage(token, message) {
  try {
    const response = await fetch(`${BASE_URL}/api/processMessage`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ message }),
    });
    return response.json();
  } catch (error) {
    throw new Error('Error');
  }
}
