# NewsAgent 前端设计规格书

**项目：** NewsAgent 移动端 UI
**日期：** 2026-04-27
**技术栈：** React 18 + Vite + TailwindCSS + GSAP
**部署：** Tailscale 内网穿透，PC 运行，手机浏览器访问
**定位：** 个人使用，Dark Aurora + Glassmorphism 风格

---

## 一、视觉系统

### 1.1 色彩变量

```css
:root {
  /* 背景 */
  --bg-deep: #0a0a0f;
  --bg-surface: #12121f;
  --bg-elevated: #1a1a2e;

  /* Aurora 极光 */
  --aurora-purple: #6366f1;
  --aurora-blue: #8b5cf6;
  --aurora-cyan: #22d3ee;

  /* 点缀 */
  --accent-warm: #f59e0b;
  --accent-rose: #f43f5e;

  /* 文字 */
  --text-primary: #f1f5f9;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;

  /* 玻璃 */
  --glass-bg: rgba(255, 255, 255, 0.05);
  --glass-border: rgba(255, 255, 255, 0.12);
  --glass-glow: rgba(99, 102, 241, 0.3);

  /* 阴影 */
  --shadow-card: 0 8px 32px rgba(0, 0, 0, 0.4);
  --shadow-glow: 0 0 20px var(--glass-glow);
}
```

### 1.2 字体

```
Display / 标题: Space Grotesk Bold (700)
正文: Inter Regular (400) / Inter Medium (500)
等宽/数据: JetBrains Mono Regular (400)
```

CDN 引入：
```html
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Inter:wght@400;500;600&family=JetBrains+Mono&display=swap" rel="stylesheet">
```

### 1.3 间距韵律

```
--space-xs:  4px
--space-sm:  8px
--space-md:  16px
--space-lg:  24px
--space-xl:  40px
--space-2xl: 64px
```

---

## 二、背景 — Aurora 极光效果

```css
.aurora-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%);
  overflow: hidden;
}

.aurora-bg::before,
.aurora-bg::after {
  content: '';
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.6;
  mix-blend-mode: screen;
  animation: aurora-drift infinite alternate;
}

.aurora-bg::before {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, #6366f1 0%, transparent 70%);
  top: -200px;
  left: -200px;
  animation-duration: 8s;
}

.aurora-bg::after {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, #8b5cf6 0%, transparent 70%);
  bottom: -150px;
  right: -150px;
  animation-duration: 12s;
  animation-delay: -4s;
}

.aurora-blob-3 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, #22d3ee 0%, transparent 70%);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation-duration: 18s;
  animation-delay: -8s;
  opacity: 0.3;
}

@keyframes aurora-drift {
  0%   { transform: translate(0, 0) scale(1); }
  33%  { transform: translate(30px, -40px) scale(1.05); }
  66%  { transform: translate(-20px, 20px) scale(0.95); }
  100% { transform: translate(40px, 30px) scale(1.02); }
}
```

---

## 三、玻璃拟态组件

### 3.1 玻璃卡片

```css
.glass-card {
  background: var(--glass-bg);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  transition: box-shadow 0.3s ease, transform 0.3s ease;
}

.glass-card:hover {
  box-shadow: var(--shadow-card), var(--shadow-glow);
  transform: translateY(-2px) scale(1.01);
}

.aurora-card:hover {
  box-shadow: var(--shadow-card), 0 0 0 1px var(--aurora-purple),
              0 0 30px rgba(99, 102, 241, 0.4);
}
```

### 3.2 玻璃底部导航栏

```css
.glass-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 72px;
  background: rgba(10, 10, 15, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-top: 1px solid var(--glass-border);
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding-bottom: env(safe-area-inset-bottom);
  z-index: 100;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: var(--text-muted);
  font-size: 10px;
  font-weight: 500;
  transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.nav-item.active {
  color: var(--text-primary);
  transform: scale(1.1);
}
```

### 3.3 玻璃输入框

```css
.glass-input {
  background: rgba(255, 255, 255, 0.07);
  backdrop-filter: blur(12px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-xl);
  padding: 14px 20px;
  color: var(--text-primary);
  font-family: 'Inter', sans-serif;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.glass-input:focus {
  border-color: var(--aurora-purple);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
}
```

---

## 四、页面结构

```
┌─────────────────────────────────────┐
│         Aurora 流动背景 (fixed)       │
├─────────────────────────────────────┤
│  内容区域 (z-index: 1)              │
│  padding-bottom: 100px            │
├─────────────────────────────────────┤
│  玻璃底部导航栏 (z-index: 100)      │
└─────────────────────────────────────┘
```

---

## 五、Tab 1: 精选（首页推荐）

**单列卡片流，卡片依次弹入。**

```jsx
// 卡片结构
<article className="glass-card aurora-card">
  <div className="card-media">
    {content.imageUrl ? (
      <img src={content.imageUrl} alt="" />
    ) : (
      <div className="card-gradient-bg" />
    )}
    <span className="card-source">{content.source}</span>
  </div>
  <div className="card-body">
    <div className="card-tags">
      {content.tags?.slice(0, 2).map(tag => (
        <span key={tag} className="tag">{tag}</span>
      ))}
    </div>
    <h3 className="card-title">{content.title}</h3>
    <p className="card-summary">{content.summary}</p>
  </div>
  <div className="card-actions">
    <button className="action-btn" onClick={() => playTts(content)}>
      🔊
    </button>
    <button className="action-btn">♥</button>
  </div>
</article>
```

**GSAP 入场动画：**

```js
gsap.from('.feed-card', {
  y: 60,
  opacity: 0,
  scale: 0.95,
  duration: 0.6,
  stagger: 0.1,
  ease: 'back.out(1.7)',
  scrollTrigger: {
    trigger: '.feed-list',
    start: 'top 80%',
  },
});
```

---

## 六、Tab 2: 搜索

```jsx
<div className="search-page">
  <div className="search-input-wrap">
    <input
      className="glass-input search-input"
      placeholder="搜索内容..."
      value={query}
      onChange={e => setQuery(e.target.value)}
    />
  </div>

  {!query && (
    <div className="search-history">
      <h4>最近搜索</h4>
      <div className="history-chips">
        {history.map(h => (
          <button key={h} className="chip glass-chip">{h}</button>
        ))}
      </div>
    </div>
  )}

  {query && results.length > 0 && (
    <div className="search-results">
      {results.map(r => (
        <article key={r.content_id} className="glass-card result-item">
          <h3>{r.title}</h3>
          <p>{r.summary}</p>
        </article>
      ))}
    </div>
  )}
</div>
```

---

## 七、Tab 3: AI 对话

**气泡式布局，用户消息右对齐（渐变背景），AI 消息左对齐（玻璃背景）。**

```jsx
<div className="chat-page">
  <div className="chat-header glass-header">
    <span>🤖 AI Assistant</span>
  </div>

  <div className="chat-messages">
    {messages.map((msg, i) => (
      <div key={i} className={`message ${msg.role}`}>
        <div className="bubble glass-bubble">{msg.content}</div>
      </div>
    ))}
  </div>

  <div className="chat-input-bar">
    <input
      className="glass-input chat-input"
      placeholder="输入消息..."
      value={input}
      onChange={e => setInput(e.target.value)}
      onKeyDown={e => e.key === 'Enter' && send()}
    />
    <button className="send-btn" onClick={send}>➤</button>
  </div>
</div>
```

```css
.message.user .bubble {
  background: linear-gradient(135deg, var(--aurora-purple), var(--aurora-blue));
  border-radius: 20px 20px 4px 20px;
  margin-left: auto;
}

.message.assistant .bubble {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 20px 20px 20px 4px;
}

.message-enter .bubble {
  animation: bubble-pop 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

---

## 八、Tab 4: 个人设置

```jsx
<div className="settings-page">
  <section className="settings-section glass-card">
    <h3>订阅主题</h3>
    <div className="topic-grid">
      {TOPICS.map(topic => (
        <button
          key={topic}
          className={`topic-chip ${selected.includes(topic) ? 'active' : ''}`}
        >
          {topic}
        </button>
      ))}
    </div>
  </section>

  <section className="settings-section glass-card">
    <h3>语音设置</h3>
    <div className="setting-row">
      <span>音色</span>
      <select className="glass-select">
        <option value="male-qn">male-qn（磁性男声）</option>
        <option value="female-qn">female-qn（温柔女声）</option>
      </select>
    </div>
  </section>
</div>
```

```css
.topic-chip.active {
  background: linear-gradient(135deg, var(--aurora-purple), var(--aurora-blue));
  border-color: transparent;
  color: white;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
}
```

---

## 九、TTS 播放态 — 声浪播放器条

底部浮现，播放时 5 条声浪波形循环起伏。

```jsx
{isPlaying && (
  <div className="tts-player glass-player">
    <div className="player-info">
      <span className="player-title">{currentTitle}</span>
      <span className="player-time">{formatTime(currentTime)} / {formatTime(duration)}</span>
    </div>
    <div className="waveform">
      {[...Array(5)].map((_, i) => (
        <div
          key={i}
          className="wave-bar"
          style={{
            animationDelay: `${i * 0.1}s`,
            height: `${20 + Math.random() * 60}%`,
          }}
        />
      ))}
    </div>
    <div className="player-controls">
      <button onClick={togglePlay}>{playing ? '⏸' : '▶'}</button>
      <button onClick={closePlayer}>✕</button>
    </div>
  </div>
)}
```

```css
.tts-player {
  position: fixed;
  bottom: 90px;
  left: 16px;
  right: 16px;
  border-radius: var(--radius-lg);
  background: rgba(10, 10, 20, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid var(--aurora-purple);
  box-shadow: 0 0 40px rgba(99, 102, 241, 0.3);
  animation: player-slide-up 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
  z-index: 90;
}

.wave-bar {
  width: 4px;
  background: linear-gradient(to top, var(--aurora-purple), var(--aurora-cyan));
  border-radius: 2px;
  animation: wave-rise 0.8s ease-in-out infinite alternate;
}

@keyframes wave-rise {
  0%   { transform: scaleY(0.3); opacity: 0.6; }
  100% { transform: scaleY(1); opacity: 1; }
}
```

---

## 十、动效总览

| 动效 | 技术实现 |
|------|---------|
| Aurora 背景流动 | CSS `@keyframes` 三层不同步 |
| 卡片弹入 | GSAP stagger + back.out(1.7) |
| 卡片悬停发光 | CSS hover + box-shadow |
| 底部播放器滑入 | CSS keyframes + back.out |
| 声浪波形 | CSS @keyframes + random height |
| 对话气泡弹出 | CSS @keyframes bubble-pop |
| 按钮点击反馈 | CSS active + scale |
| 输入框聚焦 | CSS focus + box-shadow |

---

## 十一、项目结构

```
newsagent/frontend/
├── public/
├── src/
│   ├── components/
│   │   ├── aurora/AuroraBackground.tsx
│   │   ├── ui/GlassCard.tsx, GlassInput.tsx, GlassNav.tsx
│   │   ├── feed/FeedCard.tsx, FeedList.tsx
│   │   ├── chat/ChatMessage.tsx, ChatInput.tsx
│   │   ├── search/SearchBar.tsx, SearchResults.tsx
│   │   └── settings/TopicSelector.tsx, TtsSettings.tsx
│   ├── pages/FeedPage.tsx, SearchPage.tsx, ChatPage.tsx, SettingsPage.tsx
│   ├── hooks/useTtsPlayer.ts, useApi.ts, useGsap.ts
│   ├── stores/appStore.ts  (Zustand)
│   ├── lib/api.ts
│   ├── styles/globals.css
│   ├── App.tsx
│   └── main.tsx
├── index.html
├── tailwind.config.js
├── vite.config.ts
└── package.json
```

---

## 十二、依赖

```json
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "gsap": "^3.12.5",
    "zustand": "^4.5.2",
    "axios": "^1.7.2"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.1",
    "autoprefixer": "^10.4.19",
    "postcss": "^8.4.38",
    "tailwindcss": "^3.4.4",
    "typescript": "^5.5.2",
    "vite": "^5.3.1"
  }
}
```

---

## 十三、Tailscale 配置

**PC 端：**
```bash
tailscale up
tailscale ip -4  # 记住这个 IP
cd newsagent/frontend && npm run dev -- --host 0.0.0.0 --port 5173
```

**手机端：** 安装 Tailscale App，登录同一账户，浏览器访问 `http://<Tailscale IP>:5173`

**Vite 代理配置：**

```ts
export default defineConfig({
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
```

---

## 十四、后端 API 对接

| 前端调用 | 后端端点 |
|---------|---------|
| `GET /content/recommend` | `/content/recommend` |
| `POST /content/search` | `/content/search` |
| `POST /content/tts` | `/content/tts` |
| `POST /content/summarize` | `/content/summarize` |
| `POST /query` | `/query` |
