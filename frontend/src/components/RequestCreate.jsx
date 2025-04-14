import React, { useState } from 'react';
import { Form, Input, InputNumber, Button, Select, Typography, Alert, Upload } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { createRequest, importRequest } from '../services/api';

const { Title } = Typography;
const { Option } = Select;

const RequestCreate = () => {
  const [loading, setLoading] = useState(false);
  const [serverError, setServerError] = useState('');
  const [importLoading, setImportLoading] = useState(false);
  const [importError, setImportError] = useState('');
  const [importFile, setImportFile] = useState(null);

  const [form] = Form.useForm();
  const navigate = useNavigate();

  // Function to parse comma-separated coordinates from string into an array of integers.
  const parseCoordinates = (str) => {
    return str.split(',').map((item) => parseInt(item.trim(), 10));
  };

  // Handle submission of the create request form.
  const onFinish = async (values) => {
    setLoading(true);
    setServerError('');
    const token = localStorage.getItem('token');
    if (!token) {
      setLoading(false);
      return;
    }
    const payload = {
      number_of_objects: values.number_of_objects,
      dimensions: values.dimensions,
      max_entries: values.max_entries,
      split_method: values.split_method,
      main_region_min_coordinates: parseCoordinates(values.main_region_min_coordinates),
      main_region_max_coordinates: parseCoordinates(values.main_region_max_coordinates),
    };

    try {
      await createRequest(payload, token);
      navigate('/history');
    } catch (error) {
      setLoading(false);
      const detail = error?.response?.data?.detail;
      if (Array.isArray(detail)) {
        let combinedMsg = '';
        detail.forEach((errObj) => {
          if (errObj.msg) {
            combinedMsg += errObj.msg + ' ';
          }
        });
        setServerError(combinedMsg.trim());
        const fieldsErrors = detail
          .filter((errObj) => errObj.loc && errObj.loc.length > 0)
          .map((errObj) => {
            const fieldName = errObj.loc[errObj.loc.length - 1];
            return {
              name: fieldName,
              errors: [errObj.msg || 'Invalid input'],
            };
          });
        form.setFields(fieldsErrors);
      } else if (typeof detail === 'string') {
        setServerError(detail);
      } else {
        setServerError('Failed to create request. Please check your data.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Props for the file upload component used in tree import.
  const importProps = {
    name: 'file',
    accept: '.pkl',
    beforeUpload: file => {
      setImportFile(file);
      return false;
    },
    onRemove: () => {
      setImportFile(null);
    }
  };

  // Handle the import request by sending the file to the API.
  const handleImport = async () => {
    if (!importFile) {
      setImportError('Please select a file to import.');
      return;
    }
    setImportLoading(true);
    setImportError('');
    const token = localStorage.getItem('token');
    if (!token) {
      setImportLoading(false);
      return;
    }
    try {
      await importRequest(importFile, token);
      navigate('/history');
    } catch (error) {
      setImportError('Failed to import tree.');
    } finally {
      setImportLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto mt-[var(--spacing-lg)] p-[var(--spacing-base)] bg-white shadow-lg rounded-[var(--border-radius)]">
      <Title level={2} className="mb-[var(--spacing-base)] text-center">
        Create R-TREE
      </Title>
      <Form form={form} layout="vertical" onFinish={onFinish}>
        <Form.Item
          label="Number of Objects"
          name="number_of_objects"
          rules={[{ required: true, message: 'Please input number of objects!' }]}
        >
          <InputNumber min={1} style={{ width: '100%' }} />
        </Form.Item>
        <Form.Item
          label="Dimensions"
          name="dimensions"
          rules={[{ required: true, message: 'Please input dimensions!' }]}
        >
          <InputNumber min={2} style={{ width: '100%' }} />
        </Form.Item>
        <Form.Item
          label="Max Entries"
          name="max_entries"
          rules={[{ required: true, message: 'Please input max entries!' }]}
        >
          <InputNumber min={0} style={{ width: '100%' }} />
        </Form.Item>
        <Form.Item
          label="Split Method"
          name="split_method"
          rules={[{ required: true, message: 'Please select a split method!' }]}
        >
          <Select placeholder="Select method">
            <Option value="quadratic">quadratic</Option>
            <Option value="linear">linear</Option>
          </Select>
        </Form.Item>
        <Form.Item
          label="Main Region Min Coordinates"
          name="main_region_min_coordinates"
          tooltip="Comma-separated integers, e.g. '0,2'"
          rules={[{ required: true, message: 'Please input min coordinates!' }]}
        >
          <Input placeholder="e.g. 0,2" />
        </Form.Item>
        <Form.Item
          label="Main Region Max Coordinates"
          name="main_region_max_coordinates"
          tooltip="Comma-separated integers, e.g. '2,5'"
          rules={[{ required: true, message: 'Please input max coordinates!' }]}
        >
          <Input placeholder="e.g. 2,5" />
        </Form.Item>
        {serverError && (
          <Form.Item>
            <Alert message="Error" description={serverError} type="error" showIcon />
          </Form.Item>
        )}
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} block className="rounded">
            Create
          </Button>
        </Form.Item>
      </Form>
      <div className="mt-4">
        <Title level={4}>Import R-TREE</Title>
        <Upload {...importProps} showUploadList={{ showRemoveIcon: true }}>
          <Button icon={<UploadOutlined />}>Select Tree File (.pkl)</Button>
        </Upload>
        {importError && (
          <Alert message="Error" description={importError} type="error" showIcon style={{ marginTop: '1rem' }} />
        )}
        <Button type="default" onClick={handleImport} loading={importLoading} block style={{ marginTop: '1rem' }}>
          Import Tree
        </Button>
      </div>
    </div>
  );
};

export default RequestCreate;
