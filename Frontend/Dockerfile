# Use a more specific base image for smaller size
FROM node:20-alpine

WORKDIR /app

# Copy only package files first for better caching
COPY package*.json ./
RUN npm ci --only=production  # Use ci instead of install for faster, reliable builds

# Copy only necessary files
COPY src/ ./src/
COPY public/ ./public/
COPY *.config.* ./
COPY index.html ./

EXPOSE 3000
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
