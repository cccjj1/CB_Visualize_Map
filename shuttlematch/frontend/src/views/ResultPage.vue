<template>
  <div class="result-page">
    <header class="page-header">
      <h1 class="title">🚌 查询结果</h1>
      <p class="subtitle">您的所有预约记录</p>
    </header>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      加载中...
    </div>

    <div v-else class="result-container">
      <div v-if="results.length === 0" class="no-results">
        <div class="error-icon">📭</div>
        <h2>没有找到预约记录</h2>
        <p>{{ message }}</p>
        <button @click="goBack" class="back-btn">返回预约页面</button>
      </div>

      <div v-else class="results-list">
        <div class="message-box">{{ message }}</div>
        
        <div v-for="(result, index) in results" :key="index" class="result-card">
          <div class="result-header">
            <span class="result-number">Booking #{{ index + 1 }}</span>
            <span v-if="result.matched" class="status-badge matched">✅ Matched</span>
            <span v-else-if="result.hasOwnProperty('matched')" class="status-badge failed">❌ Not Matched</span>
            <span v-else class="status-badge pending">⏳ Pending</span>
          </div>

          <div class="result-content">
            <div class="route-info">
              <div class="location">
                <span class="label">Origin</span>
                <span class="value">{{ result.origin }}</span>
              </div>
              <div class="arrow">→</div>
              <div class="location">
                <span class="label">Destination</span>
                <span class="value">{{ result.destination }}</span>
              </div>
            </div>

            <div class="time-info">
              <div v-if="result.earliest_arrival" class="time-row">
                <span class="label">Desired Arrival Time</span>
                <span class="value">{{ result.earliest_arrival }} - {{ result.latest_arrival }}</span>
              </div>
              <div v-if="result.matched" class="time-row matched-time">
                <span class="label">Pickup Time</span>
                <span class="value highlight">{{ result.pickup_time }}</span>
              </div>
              <div v-if="result.matched" class="time-row matched-time">
                <span class="label">Arrival Time</span>
                <span class="value highlight">{{ result.arrive_time }}</span>
              </div>
            </div>

            <div class="created-time">
              Submitted Time: {{ formatTime(result.created_at) }}
            </div>
          </div>
        </div>

        <button @click="goBack" class="back-btn">返回预约页面</button>
        <router-link to="/" class="back-link">返回首页</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const route = useRoute()
const results = ref([])
const loading = ref(true)
const message = ref('')

const formatTime = (datetime) => {
  if (!datetime) return '-'
  try {
    return new Date(datetime).toLocaleString('zh-CN')
  } catch {
    return datetime
  }
}

const fetchResults = async () => {
  try {
    const uid = route.query.uid
    if (!uid) {
      router.push('/')
      return
    }
    
    const response = await axios.get(`http://127.0.0.1:5001/result/${uid}`)
    results.value = response.data.results || []
    message.value = response.data.message || '查询完成'
  } catch (err) {
    console.error('查询失败:', err)
    message.value = '查询失败，请稍后重试'
    results.value = []
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/')
}

onMounted(fetchResults)
</script>

<style scoped>
.result-page {
  font-family: 'Inter', sans-serif;
  background-color: #0f1117;
  color: #e0e0e0;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  box-sizing: border-box;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px 0;
  width: 100%;
  background: linear-gradient(90deg, #4a90e2, #6a5acd);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.title {
  font-size: 2.8em;
  font-weight: 700;
  margin-bottom: 5px;
  letter-spacing: -0.03em;
}

.subtitle {
  font-size: 1.1em;
  color: #a0a0a0;
  font-weight: 400;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  color: #a0a0a0;
  font-size: 1.1em;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #3a3d4a;
  border-top: 4px solid #6a5acd;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.result-container {
  width: 100%;
  max-width: 700px;
}

.no-results {
  background-color: #1a1c23;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  text-align: center;
  border: 1px solid #2a2d36;
}

.error-icon {
  font-size: 3em;
  margin-bottom: 20px;
}

.no-results h2 {
  font-size: 1.8em;
  margin-bottom: 10px;
  color: #e0e0e0;
}

.no-results p {
  color: #a0a0a0;
  margin-bottom: 30px;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.message-box {
  background-color: #2a3a4a;
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid #4a90e2;
  color: #a0d8ff;
  font-size: 0.95em;
}

.result-card {
  background-color: #1a1c23;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  border: 1px solid #2a2d36;
  transition: all 0.3s ease;
}

.result-card:hover {
  border-color: #6a5acd;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 12px;
  border-bottom: 1px solid #3a3d4a;
}

.result-number {
  font-weight: 600;
  color: #4a90e2;
  font-size: 0.95em;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85em;
  font-weight: 500;
}

.status-badge.matched {
  background-color: #1c4a2c;
  color: #8aff80;
  border: 1px solid #2c7a3c;
}

.status-badge.pending {
  background-color: #4a3a1c;
  color: #ffd080;
  border: 1px solid #7a6a2c;
}

.status-badge.failed {
  background-color: #4a1c1c;
  color: #ff8a80;
  border: 1px solid #7a2c2c;
}

.result-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.route-info {
  display: flex;
  align-items: center;
  gap: 15px;
  background-color: #2a2d36;
  padding: 12px;
  border-radius: 8px;
}

.location {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.location .label {
  font-size: 0.85em;
  color: #c0c0c0;
}

.location .value {
  color: #e0e0e0;
  font-weight: 500;
  font-size: 0.95em;
}

.arrow {
  color: #6a5acd;
  font-size: 1.2em;
}

.time-info {
  background-color: #2a2d36;
  padding: 12px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.time-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.95em;
}

.time-row .label {
  color: #c0c0c0;
}

.time-row .value {
  color: #e0e0e0;
  font-weight: 500;
}

.time-row.matched-time .highlight {
  color: #4a90e2;
  font-weight: 600;
}

.created-time {
  font-size: 0.85em;
  color: #a0a0a0;
  text-align: right;
  font-style: italic;
}

.back-btn {
  width: 100%;
  padding: 14px 20px;
  background: linear-gradient(90deg, #4a90e2, #6a5acd);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1em;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  margin-top: 20px;
}

.back-btn:hover {
  opacity: 0.9;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4);
}

.back-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.back-link {
  display: inline-block;
  margin-top: 15px;
  padding: 12px 24px;
  background: linear-gradient(120deg, #64b5f6, #2196f3);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1em;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.back-link:hover {
  opacity: 0.9;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4);
}

.back-link:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

@media (max-width: 600px) {
  .title {
    font-size: 2.2em;
  }

  .subtitle {
    font-size: 0.9em;
  }

  .result-card {
    padding: 15px;
  }

  .route-info {
    flex-direction: column;
    gap: 10px;
  }

  .arrow {
    transform: rotate(90deg);
  }
}
</style>
