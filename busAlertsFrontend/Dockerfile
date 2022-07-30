FROM node:16

WORKDIR /app

COPY package.json /app/package.json

RUN npm install

COPY . /app

ENV BACKEND_PORT 10000

ENV IP_ADDRESS 0.0.0.0

CMD ["node", "app.js"]
