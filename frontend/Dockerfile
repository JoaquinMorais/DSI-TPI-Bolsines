FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Dev server de Vite. Para produccion conviene un build estatico servido por nginx.
CMD ["npm", "run", "dev"]
