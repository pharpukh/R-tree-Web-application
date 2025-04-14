import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Function to login a user and return the JWT token.
export async function login(username, password) {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);
  const response = await axios.post(`${API_BASE_URL}/users/login`, formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  return response.data;
}

// Function to register a new user.
export async function registerUser(email, password) {
  const response = await axios.post(
    `${API_BASE_URL}/users/register`,
    { email, password },
    { headers: { 'Content-Type': 'application/json' } }
  );
  return response.data;
}

// Function to get the list of R-tree requests for the current user.
export async function getHistory(token) {
  const response = await axios.get(`${API_BASE_URL}/requests/history`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
}

// Function to create a new R-tree request.
export async function createRequest(data, token) {
  const response = await axios.post(`${API_BASE_URL}/requests/create`, data, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
}

// Function to get the detailed information of a specific R-tree request.
export async function getRequestDetail(requestId, token) {
  const response = await axios.get(`${API_BASE_URL}/requests/${requestId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
}

// Function to download a serialized R-tree request.
export async function downloadRequest(requestId, token) {
  const response = await axios.get(`${API_BASE_URL}/requests/${requestId}/download`, {
    headers: { Authorization: `Bearer ${token}` },
    responseType: 'blob',
  });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `r_tree_${requestId}.pkl`);
  document.body.appendChild(link);
  link.click();
  link.remove();
}

// Function to perform a range query.
export async function rangeQuery(requestId, queryParams, token) {
  const response = await axios.post(`${API_BASE_URL}/requests/${requestId}/range_query`, queryParams, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
}

// Function to perform a k-NN query.
export async function knnQuery(requestId, queryParams, token) {
  const response = await axios.post(`${API_BASE_URL}/requests/${requestId}/knn_query`, queryParams, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
}

// Function to import an R-tree from a file.
export async function importRequest(file, token) {
  const formData = new FormData();
  formData.append('file', file);
  const response = await axios.post(`${API_BASE_URL}/requests/import`, formData, {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'multipart/form-data'
    },
  });
  return response.data;
}

// Function to delete an R-tree request.
export async function deleteRequest(requestId, token) {
  const response = await axios.delete(`${API_BASE_URL}/requests/${requestId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
}
