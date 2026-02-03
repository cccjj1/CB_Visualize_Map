<template>
  <div class="home-page">
    <header class="page-header">
      <h1 class="title">EvoRide</h1>
      <p class="subtitle">Smart Campus Shuttle Matching System</p>
    </header>

    <div class="button-container">
      <router-link to="/request" class="action-button submit-btn">
        <span class="emoji">📝</span>
        <span>Submit Booking Request</span>
      </router-link>
      
      <router-link to="/query" class="action-button query-btn">
        <span class="emoji">🔍</span>
        <span>Query Booking Result</span>
      </router-link>
    </div>
  </div>
</template>

<script setup>
// No additional logic needed for home page
</script>

<style scoped>
.home-page {
  font-family: 'Inter', sans-serif;
  background-color: #0f1117;
  color: #e0e0e0;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  box-sizing: border-box;
}

.page-header {
  text-align: center;
  margin-bottom: 60px;
  animation: fadeIn 0.6s ease-out;
}

.title {
  font-size: 3.5em;
  font-weight: 700;
  margin: 0;
  letter-spacing: -0.5px;
  background: linear-gradient(120deg, #64b5f6, #2196f3);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 10px;
}

.subtitle {
  font-size: 1.2em;
  color: #a0a0a0;
  font-weight: 400;
  margin: 0;
}

.button-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  max-width: 360px;
  animation: slideUp 0.8s ease-out;
}

.action-button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 18px 24px;
  color: white;
  text-decoration: none;
  border-radius: 12px;
  font-size: 1.1em;
  font-weight: 600;
  transition: all 0.3s ease;
  border: 1px solid transparent;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  gap: 12px;
}

.submit-btn {
  background: linear-gradient(120deg, #64b5f6, #2196f3);
}

.submit-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(33, 150, 243, 0.4);
}

.submit-btn:active {
  transform: translateY(-1px);
}

.query-btn {
  background: linear-gradient(120deg, #81c784, #4caf50);
}

.query-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(76, 175, 80, 0.4);
}

.query-btn:active {
  transform: translateY(-1px);
}

.emoji {
  font-size: 1.5em;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 600px) {
  .title {
    font-size: 2.5em;
  }

  .subtitle {
    font-size: 1em;
  }

  .action-button {
    padding: 16px 20px;
    font-size: 1em;
  }

  .emoji {
    font-size: 1.3em;
  }
}
</style>
