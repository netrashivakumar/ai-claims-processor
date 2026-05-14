import axios from 'axios';

const apiClient = axios.create({
  // Use the URL where your FastAPI app is running
  baseURL: 'http://localhost:8000', 
  headers: { 'Content-Type': 'application/json' },
});

export default apiClient;
