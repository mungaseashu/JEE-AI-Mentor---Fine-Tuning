# 🌐 AWS EC2 Deployment Guide - JEE Mentor AI

This guide walks you through deploying **JEE Mentor AI** on an AWS EC2 instance using Docker Compose. Since the project includes custom Dockerfiles and a `docker-compose.yml` configuration (orchestrating PostgreSQL, Redis, the FastAPI backend, and the React client through Nginx), using Docker Compose is the most robust, isolated, and scalable production method.

---

## 🛠️ Step 1: Launch an AWS EC2 Instance

1.  **Log in** to your [AWS Management Console](https://aws.amazon.com/console/).
2.  Navigate to **EC2** and click **Launch Instance**.
3.  **Choose AMI**: Select **Ubuntu Server 24.04 LTS (64-bit)**.
4.  **Select Instance Type**:
    *   *Standard CPU/Fallback Mode (Recommended for general testing)*: **`t3.medium`** (2 vCPUs, 4 GiB RAM) or **`t3.large`** (2 vCPUs, 8 GiB RAM).
    *   *GPU Mode (If running real model inference on CUDA)*: **`g4dn.xlarge`** (4 vCPUs, 16 GiB RAM, 1 NVIDIA T4 GPU).
5.  **Key Pair**: Create or select an existing key pair (`.pem` file) to SSH into the instance.
6.  **Configure Network / Security Group**:
    Create a new Security Group and configure the following **Inbound Rules**:
    
    | Port Range | Protocol | Source | Description |
    | :--- | :--- | :--- | :--- |
    | `22` | TCP | `My IP` or `0.0.0.0/0` | SSH Access |
    | `80` | TCP | `0.0.0.0/0` | HTTP Access (Nginx Frontend) |
    | `443` | TCP | `0.0.0.0/0` | HTTPS Access (Secure SSL) |
    | `8000` | TCP | `0.0.0.0/0` | FastAPI Backend API (If accessed directly) |
7.  **Storage**: Allocate at least **30 GB - 50 GB** of General Purpose SSD (gp3) root volume storage (especially if caching LLM models).
8.  Click **Launch Instance**. Once launched, allocate and associate an **Elastic IP** to this instance to ensure the public IP address doesn't change when restarting the server.

---

## 🔑 Step 2: Connect to the EC2 Instance via SSH

Open your local terminal (or Git Bash on Windows) and run:

```bash
# Locate your downloaded key pair (.pem file)
chmod 400 your-key-pair.pem

# Connect using the public IP of your EC2 instance
ssh -i "your-key-pair.pem" ubuntu@YOUR_EC2_PUBLIC_IP
```

---

## 🐳 Step 3: Install Docker and Docker Compose on Ubuntu

Run the following commands on the EC2 shell to install Docker:

```bash
# Update Ubuntu package database
sudo apt update && sudo apt upgrade -y

# Install prerequisite packages
sudo apt install -y curl apt-transport-https ca-certificates software-properties-common

# Add Docker's official GPG key
sudo fold -s
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository to APT sources
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Allow your user to run Docker commands without sudo
sudo usermod -aG docker ${USER}
# Run 'newgrp docker' or log out and log back in to apply group changes
newgrp docker

# Install Docker Compose V2
sudo apt install -y docker-compose-plugin

# Verify installations
docker --version
docker compose version
```

---

## 📂 Step 4: Clone the Codebase and Configure Environment Variables

1.  **Clone the repository** directly from your GitHub:
    ```bash
    git clone https://github.com/mungaseashu/JEE-AI-Mentor---Fine-Tuning.git
    cd JEE-AI-Mentor---Fine-Tuning
    ```
2.  **Create the production Environment file (`.env`)**:
    Create a `.env` file in the root directory:
    ```bash
    nano .env
    ```
3.  Add your production values. Note that PostgreSQL and Redis services are launched via Docker containers defined in `docker-compose.yml`. Use their container names (`db` and `redis`) as the hosts in your config:
    ```env
    # --- System Environment Configurations ---
    ENV_MODE=production
    SECRET_KEY=generate-a-secure-random-32-byte-hex-string-for-jwt

    # --- PostgreSQL Database Configuration ---
    # We reference the database container service named 'db' inside the docker network
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=yoursecurepassword
    POSTGRES_DB=jee_mentor
    DATABASE_URL=postgresql://postgres:yoursecurepassword@db:5432/jee_mentor

    # --- Redis Cache Configuration ---
    # We reference the redis container service named 'redis' inside the docker network
    REDIS_URL=redis://redis:6379/0

    # --- AI Causal Inference Model Settings ---
    BASE_MODEL_NAME=TinyLlama/TinyLlama-1.1B-Chat-v1.0
    LORA_ADAPTER_PATH=./models/adapters
    ```
    Press `CTRL+O` and `Enter` to save, then `CTRL+X` to exit nano.

---

## 🚀 Step 5: Boot the Application using Docker Compose

1.  Start the multi-container stack in detached (background) mode:
    ```bash
    docker compose up --build -d
    ```
    *This pulls the base images, builds the React frontend assets, links PostgreSQL and Redis, and launches the FastAPI ASGI server.*
2.  Verify the running status of your containers:
    ```bash
    docker compose ps
    ```
    You should see containers running for:
    *   `db` (PostgreSQL)
    *   `redis` (Caching/Limiter)
    *   `backend` (FastAPI)
    *   `frontend` (Nginx serving React SPA)
3.  Check the logs if any service crashes:
    ```bash
    docker compose logs -f backend
    ```

---

## 🌾 Step 6: Seed the RAG Knowledge Base Inside Docker

Since the vector database ChromaDB needs the primary formula revision notes seeded, execute the seeder script inside the running backend container:

```bash
docker compose exec backend python -m rag.ingest
```
*This downloads the embedding weights into the container, initializes the ChromaDB vectors, and indexes the 12 primary JEE reference cards.*

---

## 🔒 Step 7: Configure Domain Name and SSL (HTTPS) with Certbot

To secure API boundaries and make the project accessible over a custom domain (e.g. `jeementor.yourdomain.com`):

1.  Point your domain's **A Record** in your registrar (Route 53, GoDaddy, Namecheap) to the EC2 Elastic IP address.
2.  Install Certbot and python certbot nginx packages on the host machine:
    ```bash
    sudo apt install -y certbot python3-certbot-nginx
    ```
3.  Configure SSL certificates:
    ```bash
    sudo certbot --nginx -d jeementor.yourdomain.com
    ```
    Follow the prompt instructions. Certbot will automatically register the certificate and modify your Nginx routing parameters to redirect HTTP traffic to secure HTTPS.
4.  Configure certbot to auto-renew every 90 days:
    ```bash
    sudo systemctl status certbot.timer
    ```

---

## ⚙️ How to Update the Application Later

Whenever you push new updates, bug fixes, or model configurations to GitHub, pull the latest changes on your instance and rebuild:

```bash
# Pull latest code
git pull origin main

# Rebuild and restart container services
docker compose down
docker compose up --build -d

# Re-run seeder or migrations if database schemas changed
docker compose exec backend python -m rag.ingest
```
