# Build stage
FROM node:22-alpine AS builder
WORKDIR /app
COPY package.json pnpm-lock.yaml* ./
RUN npm install -g pnpm && pnpm install --frozen-lockfile
COPY . .

ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

RUN pnpm run build

# Production stage
#FROM node:22-alpine AS runner
#WORKDIR /app
#RUN npm install -g serve
#COPY --from=builder /app/dist ./dist
#EXPOSE 3000
#CMD ["serve", "-s", "dist", "-l", "3000"]


# Production stage: static files with Nginx
FROM nginx:1.25-alpine AS runner
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
