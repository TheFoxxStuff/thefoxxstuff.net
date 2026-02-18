FROM node:20-alpine AS builder
WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Эти аргументы позволят прокидывать URL API во время сборки
ARG VITE_API_BASE
ENV VITE_API_BASE=$VITE_API_BASE

RUN npm run build

FROM nginx:alpine
# Проверь, как называется папка после билда в Svelte/Vite. 
# Обычно это 'dist', а не 'build'. Если SvelteKit — может быть 'build'.
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]