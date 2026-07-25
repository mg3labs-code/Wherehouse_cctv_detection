# Railway static frontend (build Vite, serve with Caddy, proxy /api → backend)
FROM node:20-bookworm-slim AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
# Optional: set at build time — VITE_API_ORIGIN=https://your-api.up.railway.app
ARG VITE_API_ORIGIN=https://wherehousecctvdetection-production.up.railway.app
ENV VITE_API_ORIGIN=$VITE_API_ORIGIN
RUN node ./node_modules/vite/bin/vite.js build

FROM caddy:2.8-alpine
WORKDIR /srv
COPY --from=build /app/dist /srv
COPY Caddyfile /etc/caddy/Caddyfile
EXPOSE 8080
CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile"]
