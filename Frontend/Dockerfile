FROM node:20-slim

WORKDIR /app

# Install dependencies first for better cache behavior
COPY package*.json ./
RUN if [ -f package-lock.json ]; then npm ci --silent; else npm install --silent; fi

# Copy application files. The project doesn't include a `public/` folder,
# so copy the workspace rather than attempting to copy a missing directory.
COPY . .

EXPOSE 3000
# Run Vite dev server. If you use a different script in production, adjust accordingly.
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
