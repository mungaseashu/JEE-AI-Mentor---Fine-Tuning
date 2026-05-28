# ==============================================================================
# JEE MENTOR AI - FRONTEND PRODUCTION DOCKERFILE
# ==============================================================================
FROM node:18-alpine as builder

WORKDIR /app

COPY frontend/package.json ./
RUN npm install

# Copy configuration and code
COPY frontend/ .

# Build Vite project to dist/
RUN npm run build

# --- Production Serving Stage (Nginx) ---
FROM nginx:1.23-alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx config to support React Router SPAs
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
