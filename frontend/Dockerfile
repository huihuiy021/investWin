FROM node:18-alpine

WORKDIR /app

# 复制 package.json
COPY package*.json ./
RUN npm install

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 暴露端口
EXPOSE 3000

# 使用 nginx 或直接运行开发服务器
CMD ["npm", "run", "dev"]