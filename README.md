# Project Overview

## Project Description
This project is designed to manage a financial portfolio and includes services for capital gains calculations, stock portfolio management, and a web interface served by an nginx server. The project utilizes Docker for containerization and includes a MongoDB database for data storage.

---

## Project Structure

### Files and Directories

- **Members.txt**: A file containing information about the team members.
- **capital-gains/**: Directory for the service responsible for calculating capital gains.
- **nginx/**: Configuration files and resources for the nginx web server.
- **stock-portfolio/**: Directory containing the implementation of the stock portfolio management service.
- **docker-compose.yml**: A Docker Compose file to orchestrate the containers used in the project.
- **mongo-data/**: Directory for MongoDB data storage.

---

## Prerequisites

- **Docker**: Ensure Docker is installed on your system.
- **Docker Compose**: Required for managing multiple containers.

---

## Setup and Installation

1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

---

## Services Overview

### Capital Gains Service
- Calculates the capital gains for the user's financial transactions.

### Stock Portfolio Service
- Manages the user's stock portfolio, including adding, editing, and deleting stocks.

### nginx Web Server
- Serves the web interface and routes requests to the appropriate services.

### MongoDB
- Stores all persistent data, including user details, stock information, and financial transactions.

---

## Usage

1. Access the web interface via `http://localhost:80`.
2. Navigate through the services to manage your stock portfolio and view capital gains reports.

---

## Team Members
Refer to **Members.txt** for the list of contributors to this project.

---
