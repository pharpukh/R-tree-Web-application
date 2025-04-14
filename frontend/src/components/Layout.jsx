import React from 'react';
import { Layout, Menu } from 'antd';
import { HistoryOutlined, PlusOutlined, LogoutOutlined, LoginOutlined } from '@ant-design/icons';
import { Outlet, useNavigate } from 'react-router-dom';
import Logo from './Logo';

const { Header, Content, Sider, Footer } = Layout;
const MOBILE_BREAKPOINT = 768;

const AppLayout = () => {
  const navigate = useNavigate();
  const [isMobile, setIsMobile] = React.useState(false);
  const isLoggedIn = !!localStorage.getItem('token');

  // Update layout on window resize to support mobile responsiveness.
  React.useEffect(() => {
    const checkWidth = () => {
      setIsMobile(window.innerWidth < MOBILE_BREAKPOINT);
    };
    checkWidth();
    window.addEventListener('resize', checkWidth);
    return () => window.removeEventListener('resize', checkWidth);
  }, []);

  // Handle navigation based on menu item clicks.
  const onMenuClick = ({ key }) => {
    if (key === 'history' || key === 'create') {
      navigate(`/${key}`);
    } else if (key === 'logout') {
      localStorage.removeItem('token');
      navigate('/login');
    } else if (key === 'login') {
      navigate('/login');
    }
  };

  // Define menu items.
  const menuItems = [
    { key: 'history', icon: <HistoryOutlined />, label: 'History' },
    { key: 'create', icon: <PlusOutlined />, label: 'Create' },
    isLoggedIn
      ? { key: 'logout', icon: <LogoutOutlined />, label: 'Logout' }
      : { key: 'login', icon: <LoginOutlined />, label: 'Login' },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* Sidebar for desktop view */}
      {!isMobile && (
        <Sider collapsible style={{ background: 'var(--sidebar-bg)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem' }}>
            <Logo />
          </div>
          <Menu
            mode="inline"
            defaultSelectedKeys={['history']}
            onClick={onMenuClick}
            style={{ backgroundColor: 'var(--sidebar-bg)' }}
            items={menuItems}
          />
        </Sider>
      )}
      <Layout>
        {/* Header for desktop view */}
        {!isMobile && (
          <Header style={{ background: '#fff', padding: '0 var(--spacing-base)' }} />
        )}
        <Content style={{ margin: 'var(--spacing-base)', padding: 'var(--spacing-base)', background: '#fff' }}>
          {/* Outlet renders the matched child route */}
          <Outlet />
        </Content>
        {/* Footer for mobile view */}
        {isMobile && (
          <Footer style={{ padding: 0, background: 'var(--primary-color)' }}>
            <Menu
              mode="horizontal"
              defaultSelectedKeys={['history']}
              onClick={onMenuClick}
              items={menuItems}
              style={{
                display: 'flex',
                justifyContent: 'center',
                borderTop: '0.0625rem solid #ddd',
              }}
            />
          </Footer>
        )}
        {/* Footer for desktop view */}
        {!isMobile && (
          <Footer style={{ textAlign: 'center' }}>© 2025 vwm_r_tree</Footer>
        )}
      </Layout>
    </Layout>
  );
};

export default AppLayout;
