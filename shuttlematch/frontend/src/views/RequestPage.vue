<template>
  <div class="request-page">
    <div class="page-header">
      <h1>Evo<span class="accent">Ride</span></h1>
      <p class="subtitle">Your Intelligent Campus Shuttle Booking Assistant</p>
    </div>
    
    <div class="container">
      <div class="card">
        <form @submit.prevent="submitRequest" class="request-form">
          <!-- Account Input -->
          <div class="form-group account-group">
            <label for="uid">Account ID</label>
            <div class="input-wrapper">
              <input 
                id="uid"
                v-model="formData.uid"
                type="text"
                required
                placeholder="e.g., wang.18894"
                class="input-field"
              >
            </div>
          </div>

          <!-- Route Selection -->
          <div class="route-section">
            <div class="location-group">
              <div class="form-group">
                <label for="origin">Departure Location</label>
                <div class="select-wrapper">
                  <select 
                    id="origin"
                    v-model="formData.origin"
                    required
                    class="select-field"
                  >
                    <option value="">Select Departure Location</option>
                    <option v-for="location in fromLocations" :key="location" :value="location">
                      {{ location }}
                    </option>
                  </select>
                </div>
              </div>

              <div class="route-indicator">
                <div class="route-line"></div>
                <div v-if="estimatedTime" class="time-badge">
                  {{ estimatedTime }} min
                </div>
              </div>

              <div class="form-group">
                <label for="destination">Destination</label>
                <div class="select-wrapper">
                  <select 
                    id="destination"
                    v-model="formData.destination"
                    required
                    class="select-field"
                  >
                    <option value="">Select Destination</option>
                    <option v-for="location in toLocations" :key="location" :value="location">
                      {{ location }}
                    </option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <!-- Time Selection -->
          <div class="time-section">
            <div class="time-group">
              <div class="form-group">
                <label for="earliest">Earliest Arrival</label>
                <div class="input-wrapper">
                  <input 
                    id="earliest"
                    v-model="formData.earliest_arrival"
                    type="time"
                    required
                    class="time-field"
                  >
                </div>
              </div>

              <div class="time-separator">
                <span>to</span>
              </div>

              <div class="form-group">
                <label for="latest">Latest Arrival</label>
                <div class="input-wrapper">
                  <input 
                    id="latest"
                    v-model="formData.latest_arrival"
                    type="time"
                    required
                    class="time-field"
                  >
                </div>
              </div>
            </div>
          </div>

          <button type="submit" class="submit-btn" :class="{ loading: submitting }" :disabled="submitting">
            <span class="btn-text">{{ submitting ? 'Submitting...' : 'Submit Booking' }}</span>
            <div v-if="submitting" class="loading-dots">
              <span></span><span></span><span></span>
            </div>
          </button>
        </form>

        <transition name="fade">
          <div v-if="error" class="message error-message">
            {{ errorMessage }}
          </div>
        </transition>

        <transition name="fade">
          <div v-if="success" class="message success-message">
            {{ successMessage }}
          </div>
        </transition>
        
        <router-link to="/" class="back-link">Back to Home</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

export default {
  name: 'RequestPage',
  setup() {
    const router = useRouter()
    const formData = ref({
      uid: '',
      origin: '',
      destination: '',
      earliest_arrival: '',
      latest_arrival: ''
    })

    const error = ref(false)
    const errorMessage = ref('')
    const success = ref(false)
    const successMessage = ref('')
    const estimatedTime = ref(null)
    const submitting = ref(false)

    // 所有可选地点
    const allLocations = [
      'Jesse Owens Recreation Center South',
      'Ohio State University Adventure Recreation Center',
      'Morrill Tower',
      'Drackett Tower',
      'Fisher Hall',
      'Thompson Library',
      '18th Avenue Library',
      'Jennings Hall',
      'Ohio Union',
      'The City Apartment',
      'Essex Apartment',
      'Easton Town Center',
      'John Glenn Columbus International Airport',
      'Target(1717 Olentangy River Rd)'
    ].sort()

    const fromLocations = allLocations
    const toLocations = allLocations

    watch([() => formData.value.origin, () => formData.value.destination], async ([newOrigin, newDest], [oldOrigin, oldDest]) => {
      if (newOrigin && newDest) {
        try {
          const response = await axios.get(`http://127.0.0.1:5001/route_time?from=${encodeURIComponent(newOrigin)}&to=${encodeURIComponent(newDest)}`)
          estimatedTime.value = response.data.time
        } catch (err) {
          console.error('获取行程时间失败:', err)
          estimatedTime.value = null
        }
      } else {
        estimatedTime.value = null
      }
    })

    const submitRequest = async () => {
      try {
        error.value = false
        success.value = false
        submitting.value = true
        
        if (formData.value.origin === formData.value.destination) {
          error.value = true
          errorMessage.value = '出发地和目的地不能相同'
          return
        }
        
        const response = await axios.post('http://127.0.0.1:5001/match', formData.value)
        if (response.data.status === 'success') {
          success.value = true
          successMessage.value = response.data.message
          setTimeout(() => {
            router.push('/query')
          }, 3000)
        }
      } catch (err) {
        error.value = true
        if (err.response?.data?.error === 'already_submitted') {
          errorMessage.value = '您今天已经提交过预约了'
        } else if (err.response?.data?.error === 'invalid_time_range') {
          errorMessage.value = '最早到达时间必须早于最晚到达时间'
        } else if (err.response?.data?.error === 'invalid_route') {
          errorMessage.value = '不支持该路线'
        } else {
          errorMessage.value = '提交失败，请稍后重试'
        }
      } finally {
        submitting.value = false
      }
    }

    return {
      formData,
      fromLocations,
      toLocations,
      submitRequest,
      error,
      errorMessage,
      success,
      successMessage,
      estimatedTime,
      submitting
    }
  }
}
</script>

<style scoped>
.request-page {
  min-height: 100vh;
  background-color: #0f1117;
  color: #ffffff;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 24px;
}

h1 {
  font-size: 32px;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
  letter-spacing: -0.5px;
}

.accent {
  background: linear-gradient(120deg, #64b5f6, #2196f3);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  margin-top: 8px;
  font-size: 16px;
  color: #8b8c8f;
  font-weight: 400;
}

.container {
  width: 100%;
  max-width: 560px;
}

.card {
  background: #1a1c23;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.form-group {
  margin-bottom: 16px;
}

.account-group {
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.account-group label {
  text-align: center;
  margin-bottom: 8px;
}

.account-group .input-wrapper {
  width: 100%;
  max-width: 300px;
}

.account-group .input-field {
  width: 100%;
}

label {
  display: block;
  margin-bottom: 6px;
  color: #8b8c8f;
  font-weight: 500;
  font-size: 14px;
}

.input-wrapper,
.select-wrapper {
  position: relative;
  width: 100%;
}

.input-field,
.select-field,
.time-field {
  width: 100%;
  padding: 10px 12px;
  font-size: 14px;
  background-color: #2a2d36;
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  transition: all 0.2s ease;
  -webkit-appearance: none;
  appearance: none;
}

.input-field:focus,
.select-field:focus,
.time-field:focus {
  outline: none;
  border-color: #2196f3;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
}

.select-field {
  background-image: url("data:image/svg+xml,%3Csvg width='10' height='6' viewBox='0 0 10 6' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1L5 5L9 1' stroke='%238b8c8f' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  padding-right: 32px;
}

.route-section {
  background-color: #2a2d36;
  border-radius: 12px;
  padding: 20px;
  margin: 16px 0;
}

.route-indicator {
  position: relative;
  height: 40px;
  margin: 12px 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.route-line {
  width: 2px;
  height: 100%;
  background: rgba(255, 255, 255, 0.1);
  position: absolute;
}

.time-badge {
  background: linear-gradient(120deg, #64b5f6, #2196f3);
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  position: relative;
  z-index: 1;
}

.time-section {
  margin: 16px 0;
  display: flex;
  justify-content: center;
}

.time-group {
  display: grid;
  grid-template-columns: 140px 140px;
  gap: 150px;
  align-items: center;
  width: auto;
}

.time-group .form-group {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.time-group .form-group label {
  text-align: center;
  margin-bottom: 8px;
}

.time-group .input-wrapper {
  width: 100%;
}

.time-separator {
  display: none;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  font-size: 15px;
  font-weight: 600;
  color: #ffffff;
  background: linear-gradient(120deg, #64b5f6, #2196f3);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 24px;
}

.submit-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.3);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-dots {
  position: absolute;
  right: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.loading-dots span {
  width: 4px;
  height: 4px;
  background-color: #ffffff;
  border-radius: 50%;
  animation: dots 1.4s infinite ease-in-out;
}

.loading-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.loading-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes dots {
  0%, 80%, 100% { transform: scale(0); opacity: 0; }
  40% { transform: scale(1); opacity: 1; }
}

.message {
  margin-top: 16px;
  padding: 12px;
  border-radius: 8px;
  font-size: 14px;
  text-align: center;
  animation: slideIn 0.3s ease-out;
}

.error-message {
  background-color: rgba(244, 67, 54, 0.1);
  color: #f44336;
  border: 1px solid rgba(244, 67, 54, 0.2);
}

.success-message {
  background-color: rgba(76, 175, 80, 0.1);
  color: #4caf50;
  border: 1px solid rgba(76, 175, 80, 0.2);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@keyframes slideIn {
  from {
    transform: translateY(-10px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.back-link {
  display: inline-block;
  margin-top: 24px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 600;
  color: #4caf50;
  border: 1px solid #4caf50;
  border-radius: 8px;
  text-decoration: none;
  transition: all 0.2s ease;
}

.back-link:hover {
  background-color: #4caf50;
  color: #ffffff;
  border-color: #4caf50;
}

@media (max-width: 640px) {
  .page-header {
    margin-bottom: 20px;
  }

  h1 {
    font-size: 28px;
  }

  .subtitle {
    font-size: 14px;
  }

  .card {
    padding: 20px;
  }

  .time-group {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .time-separator {
    display: none;
  }
}
</style>