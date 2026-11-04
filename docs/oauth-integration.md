# OAuth 2.0 接入指南

本文档面向需要接入 cpulab 账号体系登录的第三方网站。采用标准 **Authorization Code Flow**。

```
你的用户 → 点击"用 cpulab 账号登录" → 跳转 cpulab 授权页 → 用户同意
        → 回调带回 code → 你的后端用 code 换 access_token → 调 userinfo 拿用户信息
```

## 第 0 步：注册应用

联系 cpulab 管理员注册，提供**应用名称**和**回调地址**（可多个），获得：

- `client_id`：公开标识，可以出现在前端
- `client_secret`：**仅你的后端持有**，绝不能出现在前端代码或浏览器中

> 回调地址是精确匹配的白名单，后续请求中的 `redirect_uri` 必须与注册值**完全一致**。

## 第 1 步：跳转授权页

用户点击登录按钮后，整页跳转到：

```
{CPULAB_ORIGIN}/oauth/authorize?client_id=xxx&redirect_uri=xxx&state=xxx
```

| 参数 | 说明 |
|---|---|
| `client_id` | 注册时获得 |
| `redirect_uri` | 你的回调地址，必须与注册值一致，需 URL 编码 |
| `state` | 你生成的随机串，防 CSRF。存入 session，回调时校验 |

示例（JavaScript）：

```javascript
const state = crypto.randomUUID()
sessionStorage.setItem('oauth_state', state)

const params = new URLSearchParams({
  client_id: 'YOUR_CLIENT_ID',
  redirect_uri: 'https://your-site.com/callback',
  state,
})
window.location.href = `https://cpulab.example.com/oauth/authorize?${params}`
```

用户在 cpulab 完成登录并点击"同意授权"后，浏览器跳回：

```
https://your-site.com/callback?code=xxx&state=xxx
```

用户点"拒绝"则跳回 `?error=access_denied&state=xxx`。

## 第 2 步：回调处理（你的后端）

1. 校验 `state` 与第 1 步存入的一致，不一致直接拒绝（CSRF 攻击）
2. 取出 `code`，在 **10 分钟内**用它换 token（code 一次性，用过即废）

## 第 3 步：换取 access_token（服务器对服务器）

```
POST {CPULAB_API}/api/oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&code=xxx&client_id=xxx&client_secret=xxx&redirect_uri=xxx
```

```bash
curl -X POST https://cpulab.example.com/api/oauth/token \
  -d "grant_type=authorization_code" \
  -d "code=收到的code" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "redirect_uri=https://your-site.com/callback"
```

成功响应：

```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "Bearer",
  "expires_in": 7200
}
```

## 第 4 步：获取用户信息

```
GET {CPULAB_API}/api/oauth/userinfo
Authorization: Bearer {access_token}
```

```json
{
  "user_id": 1,
  "user_name": "张三",
  "email": "zhangsan@example.com",
  "phone": "13800138000"
}
```

拿到用户信息后的登录态维护（建 session / 签你自己的 JWT）由你自行实现。

## 错误说明

所有错误统一返回 `{"message": "描述"}` + HTTP 状态码：

| 状态码 | 场景 |
|---|---|
| 400 | 参数缺失、`redirect_uri` 不在白名单、code 无效/过期 |
| 401 | `client_secret` 错误、token 缺失/过期 |
| 404 | `client_id` 未注册 |

## 注意事项

- `access_token` 有效期 2 小时，过期后需用户重新走授权流程（暂无 refresh_token）
- token 只能用于调 `userinfo`，无法访问 cpulab 的其他业务接口
- 生产环境请全程 HTTPS
