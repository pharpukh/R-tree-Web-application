import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Logout from './pages/Logout';
import AppLayout from './components/Layout';
import Requests from './components/Request';
import RequestCreate from './components/RequestCreate';
import RequestDetail from './components/RequestDetail';
const App = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route index element={<Home />} />
        <Route path="login" element={<Login />} />
        <Route path="register" element={<Register />} />
        <Route path="/" element={<AppLayout />}>
          <Route path="history" element={<Requests />} />
          <Route path="create" element={<RequestCreate />} />
          <Route path="logout" element={<Logout />} />
          <Route path="requests/:id" element={<RequestDetail />} />

        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;
