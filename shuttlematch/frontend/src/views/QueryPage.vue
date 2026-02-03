<template>
  <div class="query-page">
    <div class="page-header">
      <h1>🔍 <span class="accent">Query Booking</span></h1>
      <p class="subtitle">Enter Account ID to View Your Bookings</p>
    </div>

    <div class="form-container">
      <div class="form-card">
        <div class="form-group">
          <label for="query-uid">Account ID</label>
          <input 
            id="query-uid"
            v-model="uid"
            type="text"
            placeholder="e.g., wang.18894"
            @keyup.enter="queryResult"
            class="input-field"
          >
        </div>
        <button @click="queryResult" class="query-btn">Query Results</button>
        
        <router-link to="/" class="back-link">Back to Home</router-link>
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>Loading...</p>
    </div>

    <div v-else-if="results.length > 0" class="results-container">
      <div class="message-box">{{ message }}</div>

      <div v-for="(result, index) in results" :key="index" class="result-card">
        <div class="result-header">
          <span class="result-number">Booking #{{ index + 1 }}</span>
          <span v-if="result.matched" class="status-badge matched">✅ Matched</span>
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

          <!-- Route Map for Matched Bookings -->
          <div v-if="result.matched && result.shuttle_info" class="route-map-section">
            <div class="map-title">📍 Route Map</div>
            <img 
              :src="`http://127.0.0.1:5001/map/${result.shuttle_info.trip_id}`" 
              :alt="`Map for ${result.shuttle_info.trip_id}`"
              class="route-map-image"
              @error="handleMapError"
            >
          </div>
        </div>

        <button v-if="result.matched" @click="deleteRequest(index)" class="delete-btn">Delete Booking</button>
      </div>

      <router-link to="/" class="back-link">Back to Home</router-link>
    </div>

    <div v-else-if="errorMessage" class="no-results">
      <div class="error-icon">📭</div>
      <h2>No Booking Records Found</h2>
      <p>{{ errorMessage }}</p>
      <router-link to="/" class="back-link">Back to Home</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const uid = ref('')
const results = ref([])
const loading = ref(false)
const errorMessage = ref('')
const message = ref('')

const formatTime = (datetime) => {
  if (!datetime) return '-'
  try {
    return new Date(datetime).toLocaleString('zh-CN')
  } catch {
    return datetime
  }
}

const queryResult = async () => {
  try {
    loading.value = true
    errorMessage.value = ''
    results.value = []
    
    const response = await axios.get(`http://127.0.0.1:5001/result/${uid.value}`)
    results.value = response.data.results || []
    message.value = response.data.message || 'Query completed'
    
    if (!results.value || results.value.length === 0) {
      errorMessage.value = message.value || 'No booking records found'
    }
  } catch (err) {
    console.error('Query failed:', err)
    errorMessage.value = 'Query failed, please try again later'
    results.value = []
  } finally {
    loading.value = false
  }
}

const deleteRequest = async (index) => {
  if (!confirm('Are you sure you want to delete this booking?')) {
    return
  }
  
  try {
    loading.value = true
    await axios.delete(`http://127.0.0.1:5001/request/${uid.value}`)
    results.value.splice(index, 1)
    if (results.value.length === 0) {
      errorMessage.value = 'Booking deleted'
    }
  } catch (err) {
    console.error('Deletion failed:', err)
    alert('Failed to delete booking, please try again later')
  } finally {
    loading.value = false
  }
}

const handleMapError = (event) => {
  event.target.src = '/assets/no-map.png'; // Fallback image
  event.target.alt = 'No map available';
};
</script>

<style scoped>
.query-page {
  font-family: 'Inter', sans-serif;
  background-color: #0f1117;
  color: #e0e0e0;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
  box-sizing: border-box;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
  animation: fadeIn 0.6s ease-out;
}

.page-header h1 {
  font-size: 2.5em;
  font-weight: 700;
  margin: 0 0 10px 0;
  letter-spacing: -0.5px;
}

.accent {
  background: linear-gradient(120deg, #64b5f6, #2196f3);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  font-size: 1.1em;
  color: #a0a0a0;
  font-weight: 400;
  margin: 0;
}

.form-container {
  display: flex;
  justify-content: center;
  width: 100%;
  margin-bottom: 30px;
}

.form-card {
  background-color: #1a1c24;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  width: 100%;
  max-width: 500px;
  box-sizing: border-box;
  border: 1px solid #2a2d36;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #c0c0c0;
  font-weight: 500;
  font-size: 0.95em;
}

.input-field {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #4a4d5a;
  border-radius: 8px;
  background-color: #2a2d36;
  color: #e0e0e0;
  font-size: 1em;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.input-field:focus {
  border-color: #64b5f6;
  box-shadow: 0 0 0 3px rgba(100, 181, 246, 0.2);
  outline: none;
}

.query-btn {
  width: 100%;
  padding: 12px;
  background: linear-gradient(120deg, #64b5f6, #2196f3);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.05em;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.3);
  margin-bottom: 12px;
}

.query-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(33, 150, 243, 0.4);
}

.query-btn:active {
  transform: translateY(0);
}

.back-link {
  display: inline-block;
  margin-top: 12px;
  padding: 8px 16px;
  color: #81c784;
  text-decoration: none;
  border: 1px solid #81c784;
  border-radius: 6px;
  font-size: 0.9em;
  transition: all 0.3s ease;
  font-weight: 500;
}

.back-link:hover {
  background-color: rgba(129, 199, 132, 0.1);
  transform: translateY(-2px);
}

.loading-container {
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
  border-top-color: #64b5f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.results-container {
  width: 100%;
  max-width: 600px;
  animation: fadeIn 0.5s ease-out;
}

.message-box {
  background-color: #2a2d36;
  padding: 12px 16px;
  border-radius: 8px;
  color: #a0a0a0;
  margin-bottom: 20px;
  text-align: center;
  font-size: 0.95em;
  border-left: 4px solid #64b5f6;
}

.result-card {
  background-color: #1a1c24;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  margin-bottom: 16px;
  border: 1px solid #2a2d36;
  transition: all 0.3s ease;
}

.result-card:hover {
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.4);
  border-color: #3a3d4a;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 12px;
  border-bottom: 1px solid #2a2d36;
}

.result-number {
  font-size: 1em;
  font-weight: 600;
  color: #64b5f6;
}

.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.85em;
  font-weight: 500;
}

.status-badge.matched {
  background-color: rgba(76, 175, 80, 0.2);
  color: #81c784;
}

.status-badge.pending {
  background-color: rgba(255, 193, 7, 0.2);
  color: #ffd54f;
}

.result-content {
  margin-bottom: 15px;
}

.route-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 15px;
  padding: 12px;
  background-color: #2a2d36;
  border-radius: 8px;
}

.location {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.location .label {
  font-size: 0.75em;
  color: #a0a0a0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 2px;
}

.location .value {
  color: #e0e0e0;
  font-weight: 500;
  font-size: 0.95em;
}

.arrow {
  color: #64b5f6;
  font-size: 1.3em;
  margin: 0 15px;
  font-weight: bold;
}

.time-info {
  margin-bottom: 12px;
}

.time-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  font-size: 0.9em;
  color: #c0c0c0;
}

.time-row .label {
  color: #a0a0a0;
}

.time-row .value {
  color: #e0e0e0;
  font-weight: 500;
}

.time-row.matched-time .value.highlight {
  color: #81c784;
  font-weight: 600;
}

.created-time {
  font-size: 0.85em;
  color: #808080;
  padding-top: 8px;
  border-top: 1px solid #2a2d36;
  margin-top: 8px;
}

.route-map-section {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #3a3d4a;
}

.map-title {
  font-size: 0.9em;
  color: #64b5f6;
  margin-bottom: 8px;
  padding-bottom: 6px;
  border-bottom: 1px solid #3a3d4a;
}

.route-map-image {
  width: 100%;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.delete-btn {
  width: 100%;
  padding: 10px;
  background-color: #c62828;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.9em;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 12px;
}

.delete-btn:hover {
  background-color: #d32f2f;
  transform: translateY(-2px);
}

.delete-btn:active {
  transform: translateY(0);
}

.no-results {
  background-color: #1a1c24;
  padding: 40px;
  border-radius: 12px;
  text-align: center;
  border: 1px solid #2a2d36;
  max-width: 500px;
}

.error-icon {
  font-size: 3em;
  margin-bottom: 15px;
}

.no-results h2 {
  color: #e0e0e0;
  margin: 15px 0;
  font-size: 1.5em;
}

.no-results p {
  color: #a0a0a0;
  font-size: 0.95em;
}
</style>
