const express = require('express');
const jwt = require('jsonwebtoken');
const router = express.Router();
const admin = require('firebase-admin');
const { v4: uuidv4 } = require('uuid');

const SECRET_KEY = process.env.SECRET_KEY || 'secret';

// Firestore Initialization
const serviceAccount = require('../config/serviceAccountKey.json');
if (!admin.apps.length) {
  admin.initializeApp({
    credential: admin.credential.cert(serviceAccount),
  });
}
const db = admin.firestore();

router.post('/login', async (req, res) => {
  const { username, password } = req.body;

  if (!username || !password) {
    return res
      .status(400)
      .json({ error: 'username and password are required.' });
  }

  try {
    // Fetch user from Firestore
    const userDoc = await db.collection('users').doc(username).get();
    if (!userDoc.exists) {
      return res.status(401).json({ error: 'Invalid email or password.' });
    }

    const userData = userDoc.data();

    // Validate password
    if (userData.password !== password) {
      return res.status(401).json({ error: 'Invalid email or password.' });
    }

    // Generate sessionId and JWT token
    const sessionId = uuidv4();
    const token = jwt.sign(
      {
        role: 'User',
        sessionId,
        customerId: userData.customerId,
        email: userData.email,
      },
      SECRET_KEY,
      { expiresIn: '2h' } // Token expiry
    );

    res.status(200).json({ token });
  } catch (error) {
    console.error('Error during login:', error);
    res.status(500).json({ error: 'Internal server error.' });
  }
});

router.get('/getGuestToken', (req, res) => {
  const sessionId = uuidv4();
  const token = jwt.sign({ role: 'Guest', sessionId }, SECRET_KEY, {
    expiresIn: '2h',
  });
  res.json({ token });
});

module.exports = router;
