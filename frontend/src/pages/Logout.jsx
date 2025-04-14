import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { message } from 'antd';

const Logout = () => {
  const navigate = useNavigate();

  // On component mount, remove the token, show a logout message and redirect to home.
  useEffect(() => {
    localStorage.removeItem('token');
    message.info('You have been logged out.');
    navigate('/');
  }, [navigate]);

  return <div className="p-[var(--spacing-base)] text-center">Logging out...</div>;
};

export default Logout;
