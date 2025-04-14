import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { Spin, Alert, Form, Input, Button, Pagination } from 'antd';
import { CSSTransition } from 'react-transition-group';
import { getRequestDetail, rangeQuery, knnQuery } from '../services/api';
import './RequestDetail.css';

const PAGE_SIZE = 5;

const RequestDetail = () => {
  const { id } = useParams();
  const [requestData, setRequestData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [showImage, setShowImage] = useState(false);
  const nodeRef = useRef(null);

  const [rangeResult, setRangeResult] = useState(null);
  const [knnResult, setKnnResult] = useState(null);

  const [rangeCurrentPage, setRangeCurrentPage] = useState(1);
  const [knnCurrentPage, setKnnCurrentPage] = useState(1);

  const [rangeForm] = Form.useForm();
  const [knnForm] = Form.useForm();

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setErrorMsg('');
      const token = localStorage.getItem('token');
      if (!token) {
        setErrorMsg('No token found. Please log in.');
        setLoading(false);
        return;
      }
      try {
        const data = await getRequestDetail(id, token);
        setRequestData(data);
      } catch (error) {
        setErrorMsg('Failed to fetch request detail.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  useEffect(() => {
    if (requestData?.image_base64) {
      setTimeout(() => {
        setShowImage(true);
      }, 50);
    }
  }, [requestData]);

  const onRangeQueryFinish = async (values) => {
    const token = localStorage.getItem('token');
    if (!token) return;
    const minCoords = values.min.split(',').map(item => parseFloat(item.trim()));
    const maxCoords = values.max.split(',').map(item => parseFloat(item.trim()));
    if (minCoords.length !== requestData.dimensions || maxCoords.length !== requestData.dimensions) {
      setRangeResult({ error: 'Invalid number of coordinates. Please enter exactly ' + requestData.dimensions + ' values.' });
      return;
    }
    try {
      const result = await rangeQuery(id, { min: minCoords, max: maxCoords }, token);
      setRangeResult(result);
      setRangeCurrentPage(1);
    } catch (error) {
      setRangeResult({ error: 'Range query failed.' });
    }
  };

  const onKnnQueryFinish = async (values) => {
    const token = localStorage.getItem('token');
    if (!token) return;
    const pointCoords = values.point.split(',').map(item => parseFloat(item.trim()));
    if (pointCoords.length !== requestData.dimensions) {
      setKnnResult({ error: 'Invalid number of coordinates. Please enter exactly ' + requestData.dimensions + ' values.' });
      return;
    }
    const k = parseInt(values.k, 10);
    try {
      const result = await knnQuery(id, { point: pointCoords, k }, token);
      setKnnResult(result);
      setKnnCurrentPage(1);
    } catch (error) {
      setKnnResult({ error: 'k-NN query failed.' });
    }
  };

  if (loading) {
    return <Spin tip="Loading..." style={{ marginTop: '2rem' }} />;
  }

  if (errorMsg) {
    return <Alert type="error" message={errorMsg} style={{ marginTop: '2rem' }} />;
  }

  if (!requestData) {
    return <div>No data</div>;
  }

  const rangeObjects = rangeResult?.objects || [];
  const rangeTotal = rangeObjects.length;
  const rangeStartIndex = (rangeCurrentPage - 1) * PAGE_SIZE;
  const rangeEndIndex = rangeStartIndex + PAGE_SIZE;
  const rangeObjectsPage = rangeObjects.slice(rangeStartIndex, rangeEndIndex);

  const knnObjects = knnResult?.objects || [];
  const knnTotal = knnObjects.length;
  const knnStartIndex = (knnCurrentPage - 1) * PAGE_SIZE;
  const knnEndIndex = knnStartIndex + PAGE_SIZE;
  const knnObjectsPage = knnObjects.slice(knnStartIndex, knnEndIndex);

  return (
    <div className="request-detail-container">
      <h2>Request #{requestData.id}</h2>
      <p><b>Objects:</b> {requestData.number_of_objects}</p>
      <p><b>Dimensions:</b> {requestData.dimensions}</p>
      <p><b>Max Entries:</b> {requestData.max_entries}</p>
      <p><b>Split Method:</b> {requestData.split_method}</p>
      <p><b>Created At:</b> {new Date(requestData.created_at).toLocaleString()}</p>

      {requestData.image_base64 && (
        <div style={{ marginTop: '1rem' }}>
          <h3>R-Tree Visualization</h3>
          <CSSTransition
            in={showImage}
            timeout={300}
            classNames="fade"
            unmountOnExit
            nodeRef={nodeRef}
          >
            <img
              ref={nodeRef}
              src={`data:image/png;base64,${requestData.image_base64}`}
              alt="R-tree"
              style={{ maxWidth: '100%', border: '1px solid #ccc' }}
            />
          </CSSTransition>
        </div>
      )}

      <div style={{ marginTop: '2rem' }}>
        <h3>Range Query</h3>
        <Form form={rangeForm} layout="vertical" onFinish={onRangeQueryFinish}>
          <Form.Item
            name="min"
            label="Min Query Coordinates (comma-separated)"
            rules={[{ required: true, message: 'Please input min query coordinates' }]}
          >
            <Input placeholder="e.g., 0,0" />
          </Form.Item>
          <Form.Item
            name="max"
            label="Max Query Coordinates (comma-separated)"
            rules={[{ required: true, message: 'Please input max query coordinates' }]}
          >
            <Input placeholder="e.g., 10,5" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit">
              Run Range Query
            </Button>
          </Form.Item>
        </Form>
        {rangeResult && (
          <div style={{ marginTop: '1rem' }}>
            {rangeResult.error ? (
              <Alert type="error" message={rangeResult.error} />
            ) : (
              <>
                <h4>Range Query Results</h4>
                <p>Visited Nodes: {rangeResult.visited}</p>
                <p>Found {rangeResult.objects.length} objects.</p>
                <ul className="scrollable-list">
                  {rangeObjectsPage.map((obj, idx) => (
                    <li key={idx + rangeStartIndex}>{JSON.stringify(obj)}</li>
                  ))}
                </ul>
                {rangeTotal > PAGE_SIZE && (
                  <Pagination
                    current={rangeCurrentPage}
                    pageSize={PAGE_SIZE}
                    total={rangeTotal}
                    onChange={(page) => setRangeCurrentPage(page)}
                    style={{ marginTop: '1rem', display: 'flex', justifyContent: 'center' }}
                  />
                )}
                {rangeResult.graph && (
                  <div>
                    <h4>Algorithm Comparison Graph</h4>
                    <img
                      src={`data:image/png;base64,${rangeResult.graph}`}
                      alt="Range Query Graph"
                      style={{ maxWidth: '100%', border: '1px solid #ccc' }}
                    />
                  </div>
                )}
                {rangeResult.time_graph && (
                  <div>
                    <h4>Query Execution Time Graph</h4>
                    <img
                      src={`data:image/png;base64,${rangeResult.time_graph}`}
                      alt="Range Query Time Graph"
                      style={{ maxWidth: '100%', border: '1px solid #ccc' }}
                    />
                  </div>
                )}
                {requestData.dimensions === 2 && rangeResult.visualization && (
                  <div>
                    <h4>Range Query Visualization</h4>
                    <img
                      src={`data:image/png;base64,${rangeResult.visualization}`}
                      alt="Range Query Visualization"
                      style={{ maxWidth: '100%', border: '1px solid #ccc' }}
                    />
                  </div>
                )}
                <p>
                  Results match between R-tree and Sequential:{' '}
                  {rangeResult.match ? 'YES' : 'NO'}
                </p>
              </>
            )}
          </div>
        )}
      </div>

      <div style={{ marginTop: '2rem' }}>
        <h3>k-NN Query</h3>
        <Form form={knnForm} layout="vertical" onFinish={onKnnQueryFinish}>
          <Form.Item
            name="point"
            label="Query Point Coordinates (comma-separated)"
            rules={[{ required: true, message: 'Please input query point coordinates' }]}
          >
            <Input placeholder="e.g., 0,0" />
          </Form.Item>
          <Form.Item
            name="k"
            label="k (number of nearest neighbors)"
            rules={[{ required: true, message: 'Please input k' }]}
          >
            <Input placeholder="e.g., 3" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit">
              Run k-NN Query
            </Button>
          </Form.Item>
        </Form>
        {knnResult && (
          <div style={{ marginTop: '1rem' }}>
            {knnResult.error ? (
              <Alert type="error" message={knnResult.error} />
            ) : (
              <>
                <h4>k-NN Query Results</h4>
                <p>Visited Nodes: {knnResult.visited}</p>
                <p>Found {knnResult.objects.length} objects.</p>
                <ul className="scrollable-list">
                  {knnObjectsPage.map((obj, idx) => (
                    <li key={idx + knnStartIndex}>
                      {JSON.stringify(obj)} - Distance: {knnResult.distances[idx + knnStartIndex].toFixed(2)}
                    </li>
                  ))}
                </ul>
                {knnTotal > PAGE_SIZE && (
                  <Pagination
                    current={knnCurrentPage}
                    pageSize={PAGE_SIZE}
                    total={knnTotal}
                    onChange={(page) => setKnnCurrentPage(page)}
                    style={{ marginTop: '1rem', display: 'flex', justifyContent: 'center' }}
                  />
                )}
                {knnResult.graph && (
                  <div>
                    <h4>Algorithm Comparison Graph</h4>
                    <img
                      src={`data:image/png;base64,${knnResult.graph}`}
                      alt="k-NN Query Graph"
                      style={{ maxWidth: '100%', border: '1px solid #ccc' }}
                    />
                  </div>
                )}
                {knnResult.time_graph && (
                  <div>
                    <h4>Query Execution Time Graph</h4>
                    <img
                      src={`data:image/png;base64,${knnResult.time_graph}`}
                      alt="k-NN Query Time Graph"
                      style={{ maxWidth: '100%', border: '1px solid #ccc' }}
                    />
                  </div>
                )}
                {requestData.dimensions === 2 && knnResult.visualization && (
                  <div>
                    <h4>k-NN Query Visualization</h4>
                    <img
                      src={`data:image/png;base64,${knnResult.visualization}`}
                      alt="k-NN Query Visualization"
                      style={{ maxWidth: '100%', border: '1px solid #ccc' }}
                    />
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default RequestDetail;
