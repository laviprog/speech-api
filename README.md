# Speech API

Speech API is a fast and fault-tolerant service for working with STT. Related
project: [Speech Admin](https://github.com/laviprog/speech-admin)

![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)

## 🛠️ Getting Started

Follow the steps below to set up and run the Speech API using Docker (with optional
GPU acceleration).

### ⚙️ Configure Environment Variables

Copy the example environment file and fill in the necessary values:

```bash
cp .env.example .env
```

Edit the `.env` file to set your environment variables. You can use the default values or customize
them as needed.

### 🐳 Build and Run the Docker Container

#### Using CPU:

Start the Docker container with the following command:

```bash
docker compose up --build -d
```

This command will build the Docker image and start the container.

#### Using GPU:

Set up the `docker-compose.yml` file to use GPU acceleration.

```bash
docker compose up --build -d
```

This command will build the Docker image and start the container with GPU support.

Then, API will be available at `http://localhost:8080`.

Documentation will be available at `http://localhost:8080/docs`.
