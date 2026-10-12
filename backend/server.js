const express = require('express');
const cors = require('cors');
require('dotenv').config();

const ragRoutes = require('./routes/ragRoutes');
const claimRoutes = require('./routes/claimRoutes');

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

// Routes
app.use('/api/rag', ragRoutes);
app.use('/api/claims', claimRoutes);

app.get('/api/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date(),
    service: 'healthcare-rag-backend'
  });
});

app.listen(PORT, () => {
  console.log(`[Express Backend] Server running on http://localhost:${PORT}`);
});
