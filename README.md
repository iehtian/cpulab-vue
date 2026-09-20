# cpulab

CPU 实验室管理平台（前后端分离 monorepo）。

## 目录结构

```
cpulab-vue/
├── frontend/   # Vue 3 + Vite + TypeScript 前端
├── backend/   # Flask 后端（待补充）
├── .gitignore
└── README.md
```

## 前端

技术栈：Vue 3 · Vite · TypeScript · Pinia · Vue Router · Element Plus · Axios

```sh
cd frontend
npm install
npm run dev        # 开发服务器，/api 代理到 http://localhost:8010
npm run build      # 类型检查 + 生产构建
npm run test:unit  # 单元测试（Vitest）
```

推荐 IDE：[VS Code](https://code.visualstudio.com/) + [Vue (Official)](https://marketplace.visualstudio.com/items?itemName=Vue.volar)（禁用 Vetur）。

## 后端

Flask 服务（待补充）。开发约定监听 `http://localhost:8010`，与前端 Vite 代理对齐，见 [frontend/vite.config.ts](frontend/vite.config.ts)。

```sh
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask run --port 8010
```
