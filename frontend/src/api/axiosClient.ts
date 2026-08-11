import axios from 'axios';
import { toast } from 'react-hot-toast';

const API_BASE_URL = 'http://localhost:8000';

export const axiosClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

axiosClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // We can handle generic errors here or let the thunk handle them.
    // For now, we'll let the thunk trigger the specific UI toasts.
    if (!error.response) {
      toast.error("Couldn't reach the server — try again");
    }
    return Promise.reject(error);
  }
);
