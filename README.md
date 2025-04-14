# R-Tree 

## Overview

This project is a full-stack web application for managing and executing spatial queries using an R-Tree data structure. The backend is built with FastAPI, SQLAlchemy, and PostgreSQL, while the frontend is developed using React, Vite, Ant Design, and Tailwind CSS. The application allows users to:
- Register, log in, and log out.
- Create and manage R-Tree requests by specifying parameters (number of objects, dimensions, max entries, split method, and region boundaries).
- Import and delete R-Tree requests.
- Execute spatial queries such as range queries and k-NN queries.
- Visualize the R-Tree structure and query results, with detailed comparison graphs for algorithm performance (for 2D trees).

## Prerequisites

Before running the application, ensure you have the following installed on your machine:
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

No additional dependencies need to be installed on your host machine as Docker containers will encapsulate all necessary libraries.

## Running the Application

1. **Clone the Repository and build app:**

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   docker-compose up --build -d

2. **How to use**
 - Open http://localhost:3000/ in your browser