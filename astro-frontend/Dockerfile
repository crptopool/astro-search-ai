FROM node:22-alpine

WORKDIR /app

COPY package.json pnpm-lock.yaml* ./
RUN npm install -g pnpm && pnpm install --frozen-lockfile

COPY . .

RUN pnpm build

# Entrypoint is set by docker-compose command
EXPOSE 3000