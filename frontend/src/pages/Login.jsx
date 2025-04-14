import React, { useState } from 'react';
import { Form, Input, Button, Typography, Alert } from 'antd';
import { useNavigate } from 'react-router-dom';
import { login } from '../services/api';

const { Title, Text } = Typography;

const Login = () => {
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const navigate = useNavigate();

  // Handle form submission for login.
  const onFinish = async (values) => {
    setLoading(true);
    setErrorMessage('');
    try {
      const data = await login(values.email, values.password);
      localStorage.setItem('token', data.access_token);
      navigate('/');
    } catch (error) {
      const detail = error.response?.data?.detail;
      const msg = detail || 'Login failed. Please check your credentials.';
      setErrorMessage(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto mt-[var(--spacing-lg)] p-[var(--spacing-base)] bg-white shadow-lg rounded-[var(--border-radius)]">
      <Button type="link" onClick={() => navigate('/')} className="mb-[var(--spacing-base)]">
        ← Back
      </Button>
      <Title level={2} className="mb-[var(--spacing-base)] text-center">Login</Title>
      <Form name="login_form" onFinish={onFinish} layout="vertical">
        <Form.Item
          label="Email"
          name="email"
          rules={[{ required: true, message: 'Please input your email!' }]}
        >
          <Input placeholder="Enter your email" className="rounded" />
        </Form.Item>
        <Form.Item
          label="Password"
          name="password"
          rules={[{ required: true, message: 'Please input your password!' }]}
        >
          <Input.Password placeholder="Enter your password" className="rounded" />
        </Form.Item>
        {errorMessage && (
          <Form.Item>
            <Alert message={errorMessage} type="error" showIcon />
          </Form.Item>
        )}
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} block className="rounded">
            Log In
          </Button>
        </Form.Item>
      </Form>
      <div className="text-center">
        <Text>Don't have an account?</Text>
        <Button type="link" onClick={() => navigate('/register')}>
          Register Now
        </Button>
      </div>
    </div>
  );
};

export default Login;
