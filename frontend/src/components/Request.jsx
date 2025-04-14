import React, { useState, useEffect } from 'react';
import { Table, message, Button, Modal } from 'antd';
import { getHistory, downloadRequest, deleteRequest } from '../services/api';
import { useNavigate } from 'react-router-dom';

const Requests = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // Fetch the history of requests for the current user.
  const fetchHistory = async () => {
    setLoading(true);
    const token = localStorage.getItem('token');
    if (!token) {
      message.warning('No token found. Please log in.');
      setLoading(false);
      return;
    }
    try {
      const result = await getHistory(token);
      setData(result);
    } catch (error) {
      message.error('Failed to fetch request history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  // Navigate to request detail page.
  const handleViewDetail = (id) => {
    navigate(`/requests/${id}`);
  };

  // Trigger download of the serialized R-tree.
  const handleDownload = (id) => {
    const token = localStorage.getItem('token');
    if (!token) {
      message.warning('No token found. Please log in.');
      return;
    }
    downloadRequest(id, token);
  };

  // Delete a request after confirmation.
  const handleDelete = (id) => {
    Modal.confirm({
      title: 'Confirm Deletion',
      content: 'Are you sure you want to delete this request?',
      okText: 'Yes',
      cancelText: 'No',
      onOk: async () => {
        const token = localStorage.getItem('token');
        if (!token) {
          message.warning('No token found. Please log in.');
          return;
        }
        try {
          await deleteRequest(id, token);
          message.success('Request deleted successfully.');
          fetchHistory();
        } catch (error) {
          message.error('Failed to delete request.');
        }
      },
    });
  };

  // Define columns for the Ant Design Table.
  const columns = [
    {
      title: 'Objects',
      dataIndex: 'number_of_objects',
      key: 'number_of_objects',
      align: 'center',
      width: 100,
    },
    {
      title: 'Dimensions',
      dataIndex: 'dimensions',
      key: 'dimensions',
      align: 'center',
      width: 100,
    },
    {
      title: 'Method',
      dataIndex: 'split_method',
      key: 'split_method',
      align: 'center',
      width: 120,
    },
    {
      title: 'Created At',
      dataIndex: 'created_at',
      key: 'created_at',
      align: 'center',
      width: 180,
      render: (text) => new Date(text).toLocaleString(),
    },
    {
      title: 'Action',
      key: 'action',
      align: 'center',
      width: 200,
      render: (_, record) => (
        <>
          <Button type="link" onClick={() => handleViewDetail(record.id)}>
            View
          </Button>
          <Button type="link" onClick={() => handleDownload(record.id)}>
            Download
          </Button>
          <Button type="link" danger onClick={() => handleDelete(record.id)}>
            Delete
          </Button>
        </>
      ),
    },
  ];

  const paginationConfig = {
    pageSize: 5,
    position: ['bottomCenter'],
    hideOnSinglePage: false,
  };

  return (
    <div style={{ padding: '1rem' }}>
      <h2 style={{ marginBottom: '1rem', fontWeight: 'bold', fontSize: '1.25rem' }}>
        R-TREE History
      </h2>
      <Table
        columns={columns}
        dataSource={data}
        loading={loading}
        rowKey="id"
        bordered
        size="middle"
        pagination={paginationConfig}
        tableLayout="fixed"
        scroll={{ x: 650 }}
      />
    </div>
  );
};

export default Requests;
