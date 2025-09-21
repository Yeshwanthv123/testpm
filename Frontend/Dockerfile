# frontend/Dockerfile
FROM node:20-slim
WORKDIR /app

# Install deps
COPY package*.json ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

# Copy the rest of the app
COPY . .

EXPOSE 3000
# Vite dev server (change to npm start if your script is "start")
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
