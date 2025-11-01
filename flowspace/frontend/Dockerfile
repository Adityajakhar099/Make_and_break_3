# ==== Frontend Dockerfile ====
FROM node:18-alpine

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy frontend source
COPY . .

EXPOSE 3000

# Run development server
CMD ["npm", "run", "dev"]
