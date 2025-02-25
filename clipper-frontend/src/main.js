import "bootstrap/dist/css/bootstrap.min.css"
import "bootstrap"
import axios from 'axios'

import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import ExplorePage from './pages/ExplorePage.vue'
import SearchPage from './pages/SearchPage.vue'

// set axios base url
axios.defaults.baseURL = 'http://localhost:5000'

const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: '/', name: "explore", component: ExplorePage },
        { path: '/search', name: "search", component: SearchPage },
    ]
})

createApp(App).use(router).mount('#app')
