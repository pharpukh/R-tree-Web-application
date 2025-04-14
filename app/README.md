# R-Tree Backend 

This backend of R-Tree web application built with FastAPI for managing and processing spatial queries using an R-Tree data structure. The application allows users to create, import, delete, and execute spatial queries (range and k-NN queries) on generated R-Trees. It also provides visualization and performance comparison graphs.

## Features

- **User Authentication:**  
  Users can register and log in using JWT-based authentication.
  
- **R-Tree Management:**  
  Users can create new R-Tree requests with custom parameters (number of objects, dimensions, max entries, split method, and region boundaries). The R-Tree is built and serialized (using pickle) to be stored in the database.

- **Import & Delete:**  
  Users have the option to import an existing R-Tree from a file and delete any of their R-Tree requests.

- **Spatial Queries:**  
  The application supports two types of spatial queries:
  - **Range Query:** Find all objects whose bounding boxes overlap with a given query region.
  - **k-NN Query:** Find the k nearest neighbors to a given point.
  
- **Visualization & Experimentation:**  
  For two-dimensional trees, the backend generates visualizations using matplotlib. It also performs experiments to compare the efficiency of the R-Tree query against a sequential search and returns graphs (encoded as base64 images).

## Project Structure

- **app/config:**  
  Contains configuration settings and security functions for password hashing and JWT token creation.

- **app/db:**  
  Contains the database configuration, including the Base class for models, session management, and database helpers.

- **app/user:**  
  Contains user-related models, schemas, CRUD operations, and endpoints for registration and login.

- **app/request:**  
  Contains the model for R-Tree requests, Pydantic schemas for request creation and output, and CRUD operations for managing requests.

- **app/services/r_tree.py:**  
  Implements the R-Tree data structure with methods for insertion, node splitting (both quadratic and linear), range queries, and k-NN queries.

- **app/services/visualization.py:**  
  Contains functions for generating 2D visualizations and line graphs (comparison of R-Tree and sequential search performance).

- **app/services/queries.py:**  
  Contains functions for running experiments to collect data for spatial queries across different database sizes.

## Configuration

- Environment variables are loaded from the .env file located at the root of the project. Ensure you have the following variables defined:

- API_V1_PREFIX – API prefix for versioning.

- DB_URL – Database connection URL.

- DB_ECHO – Flag to enable SQLAlchemy query echo (e.g., True or False).

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
