import axios from 'axios';

const API_URL = 'http://10.56.63.66:5001';  // ← your Mac IP from Flask output (change if different)

export const getLots = async () => {
  try {
    const res = await axios.get(`${API_URL}/lots`);
    return res.data;
  } catch (err) {
    console.error('Fetch lots failed:', err);
    return [];
  }
};

export const submitReport = async (lotName, status, reporter = 'guest') => {
  try {
    const res = await axios.post(`${API_URL}/report`, {
      lot_name: lotName,
      status,
      reporter,
    });
    return res.data;
  } catch (err) {
    console.error('Report failed:', err);
    throw err;
  }
};