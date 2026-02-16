# Этап 1: Сборка (самый тяжелый этап)
FROM node:20-alpine as build-stage

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Этап 2: Раздача статики через Nginx
FROM nginx:stable-alpine

# Копируем только результат сборки (папка dist или build)
# Проверь в svelte.config.js куда идет билд (обычно /app/build или /app/dist)
COPY --from=build-stage /app/build /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]