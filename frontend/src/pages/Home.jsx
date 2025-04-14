import React from 'react';
import { Menu, Button } from 'antd';
import { HistoryOutlined, PlusOutlined, LogoutOutlined, LoginOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import Logo from '../components/Logo';

const Home = () => {
  const navigate = useNavigate();
  const isLoggedIn = !!localStorage.getItem('token');

  // Handle menu item clicks
  const onMenuClick = ({ key }) => {
    if (key === 'history') {
      navigate('/history');
    } else if (key === 'create') {
      navigate('/create');
    }
  };

  // Handle logout and login actions
  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };
  const handleLogin = () => {
    navigate('/login');
  };

  return (
    <div
      className="flex flex-col items-center justify-center min-h-screen bg-[var(--secondary-bg)] px-[var(--spacing-base)]"
    >
      {/* Display logo */}
      <div className="mb-[var(--spacing-base)]">
        <Logo/>
      </div>
      <div className="w-full max-w-xs">
        <Menu
          onClick={onMenuClick}
          mode="vertical"
          className="w-full"
          items={[
            { key: 'history', icon: <HistoryOutlined/>, label: 'History' },
            { key: 'create', icon: <PlusOutlined/>, label: 'Create R-TREE' },
          ]}
        />
        <div className="mt-[var(--spacing-base)]">
          {isLoggedIn ? (
            <Button type="primary" icon={<LogoutOutlined/>} block onClick={handleLogout}>
              Logout
            </Button>
          ) : (
            <Button type="primary" icon={<LoginOutlined/>} block onClick={handleLogin}>
              Login
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

export default Home;
