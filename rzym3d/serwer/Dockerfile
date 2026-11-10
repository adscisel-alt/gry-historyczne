# Serwer gry online „Roman Empire” (przekaźnik pokoi na WebSocket) – ten sam projekt Godota w trybie --serwer.
# Budowa (z katalogu rzym3d):   docker build -f serwer/Dockerfile -t roman-empire-serwer .
# Uruchomienie:                 docker run -p 9080:9080 roman-empire-serwer
# Dla gry w przeglądarce ze strony https potrzebny jest adres wss:// – postaw serwer za odwrotnym proxy
# z certyfikatem (np. Caddy, nginx) albo na hostingu, który sam dodaje TLS (Render, Fly.io, Railway…).
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl unzip ca-certificates libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*
RUN curl -sSL -o /tmp/godot.zip https://github.com/godotengine/godot/releases/download/4.3-stable/Godot_v4.3-stable_linux.x86_64.zip \
    && unzip -q /tmp/godot.zip -d /opt && mv /opt/Godot_v4.3-stable_linux.x86_64 /usr/local/bin/godot && rm /tmp/godot.zip
COPY godot/project.godot godot/icon.png /gra/
COPY godot/skrypty /gra/skrypty
COPY godot/sceny /gra/sceny
COPY godot/dane /gra/dane
RUN godot --headless --path /gra --import || true
ENV PORT=9080
EXPOSE 9080
CMD ["sh", "-c", "godot --headless --path /gra -- --serwer ${PORT}"]
