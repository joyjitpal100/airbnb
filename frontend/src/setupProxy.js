const express = require('express');
const path = require('path');

module.exports = function(app) {
  // Serve static files from /app for all non-React routes
  app.use((req, res, next) => {
    // Skip webpack dev server internal routes
    if (req.url.startsWith('/sockjs-node') || req.url.startsWith('/ws') || req.url === '/') {
      return next();
    }

    const filePath = path.join('/app', req.url);
    res.sendFile(filePath, (err) => {
      if (err) next();
    });
  });
};
