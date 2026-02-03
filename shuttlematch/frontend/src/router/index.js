import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import RequestPage from '../views/RequestPage.vue'
import ResultPage from '../views/ResultPage.vue'
import QueryPage from '../views/QueryPage.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage
  },
  {
    path: '/request',
    name: 'Request',
    component: RequestPage
  },
  {
    path: '/result',
    name: 'Result',
    component: ResultPage
  },
  {
    path: '/query',
    name: 'Query',
    component: QueryPage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
