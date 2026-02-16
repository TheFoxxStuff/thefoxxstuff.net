FROM node:20-alpine AS builder
WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

ARG VITE_API_BASE=https://api.thefoxxstuff.net/api
ENV VITE_API_BASE=$VITE_API_BASE
ENV NODE_OPTIONS="--max-old-space-size=1024"

RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
