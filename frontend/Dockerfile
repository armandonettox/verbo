# Build a partir da pasta frontend: docker build -t verbo-frontend frontend
FROM node:24-alpine AS build
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# nginx sem root, escutando na 8080. O arquivo .template recebe as variaveis de
# ambiente (ex: BACKEND_URL) quando o container sobe.
FROM nginxinc/nginx-unprivileged:alpine
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html

ENV BACKEND_URL=http://verbo-backend:8000
# Faz a imagem preencher NGINX_LOCAL_RESOLVERS com o DNS do container, usado no `resolver`
# do nginx.conf.template para resolver o backend a cada requisicao
ENV NGINX_ENTRYPOINT_LOCAL_RESOLVERS=1
EXPOSE 8080
