const express = require('express');
const jwt = require('jsonwebtoken');
const router = express.Router();
const axios = require('axios');

const SECRET_KEY = process.env.SECRET_KEY || 'secret';

/**
 * Middleware to Validate JWT
 */
const validateToken = (req, res, next) => {
  //   const token = req.headers['authorization'];
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) {
    return res.status(403).json({ error: 'No token provided.' });
  }

  try {
    const decoded = jwt.verify(token, SECRET_KEY);
    let sessionData = {};
    if (decoded.role === 'User') {
      sessionData = {
        isAuthenticated: true,
        sessionId: decoded.sessionId,
        customerId: decoded.customerId,
        email: decoded.email,
      };
    } else if (decoded.role === 'Guest') {
      sessionData = {
        isAuthenticated: false,
        sessionId: decoded.sessionId,
      };
    }
    req.sessionData = sessionData;
    next();
  } catch (error) {
    console.error('Invalid token:', error);
    res.status(401).json({ error: 'Unauthorized. Invalid token.' });
  }
};

router.post('/processMessage', validateToken, async (req, res) => {
  try {
    console.log(req.sessionData);
    const { message } = req.body;

    const externalApiUrl = 'https://shop.migage.com/chat';
    const externalResponse = await axios.post(externalApiUrl, {
      chatMessage: message,
      isAuthenticated: req.sessionData.isAuthenticated,
      customerId: req.sessionData.customerId,
      sessionId: req.sessionData.sessionId,
    });
    console.log(externalResponse);
    res.status(200).json({ response: externalResponse.data.response });
  } catch (error) {
    console.log(error);
    res.status(401).json({ error: 'Invalid token' });
  }
});

module.exports = router;
