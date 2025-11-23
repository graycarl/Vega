<script setup>
import { ref, onMounted } from 'vue'

const status = ref('loading')
const backendHealth = ref(null)

onMounted(async () => {
  try {
    const response = await fetch('http://localhost:8000/health')
    backendHealth.value = await response.json()
    status.value = 'ok'
  } catch (error) {
    console.error('Failed to fetch backend health:', error)
    status.value = 'error'
  }
})
</script>

<template>
  <div class="app">
    <header class="header">
      <h1>🚀 Vega Gateway</h1>
      <p>LLM API Gateway 网关系统</p>
    </header>
    
    <main class="main">
      <div class="welcome-card">
        <h2>欢迎使用 Vega Gateway</h2>
        <p>统一的 LLM API 网关，提供代理、限流、配置管理和用量统计</p>
        
        <div class="status-section">
          <h3>系统状态</h3>
          <div :class="['status-indicator', status]">
            <span v-if="status === 'loading'">⏳ 检测中...</span>
            <span v-else-if="status === 'ok'">✅ 运行正常</span>
            <span v-else>❌ 连接失败</span>
          </div>
          
          <div v-if="backendHealth" class="health-info">
            <p><strong>后端服务:</strong> {{ backendHealth.service }}</p>
            <p><strong>版本:</strong> {{ backendHealth.version }}</p>
            <p><strong>时间:</strong> {{ backendHealth.timestamp }}</p>
          </div>
        </div>

        <div class="quick-links">
          <h3>快速链接</h3>
          <ul>
            <li><a href="http://localhost:8000/docs" target="_blank">📚 API 文档</a></li>
            <li><a href="http://localhost:8000/health" target="_blank">❤️ 健康检查</a></li>
            <li><a href="https://github.com/graycarl/vega" target="_blank">🔧 GitHub 仓库</a></li>
          </ul>
        </div>
      </div>
    </main>
    
    <footer class="footer">
      <p>Vega Gateway v0.1.0 | Powered by FastAPI + Vue.js</p>
    </footer>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.header h1 {
  margin: 0;
  font-size: 2.5rem;
}

.header p {
  margin: 0.5rem 0 0 0;
  opacity: 0.9;
}

.main {
  flex: 1;
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
}

.welcome-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}

.welcome-card h2 {
  margin-top: 0;
  color: #333;
}

.status-section {
  margin: 2rem 0;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.status-indicator {
  padding: 1rem;
  border-radius: 6px;
  margin: 1rem 0;
  font-weight: 600;
}

.status-indicator.loading {
  background: #fff3cd;
  color: #856404;
}

.status-indicator.ok {
  background: #d4edda;
  color: #155724;
}

.status-indicator.error {
  background: #f8d7da;
  color: #721c24;
}

.health-info {
  margin-top: 1rem;
  padding: 1rem;
  background: white;
  border-radius: 6px;
  font-size: 0.9rem;
}

.health-info p {
  margin: 0.5rem 0;
}

.quick-links {
  margin-top: 2rem;
}

.quick-links h3 {
  margin-top: 0;
}

.quick-links ul {
  list-style: none;
  padding: 0;
}

.quick-links li {
  margin: 0.5rem 0;
}

.quick-links a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s;
}

.quick-links a:hover {
  color: #764ba2;
  text-decoration: underline;
}

.footer {
  background: #f8f9fa;
  padding: 1rem;
  text-align: center;
  color: #666;
  border-top: 1px solid #e0e0e0;
}
</style>
