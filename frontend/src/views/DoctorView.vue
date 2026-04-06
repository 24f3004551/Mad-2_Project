<template>
  <div>
    <nav class="navbar navbar-expand-lg bg-warning">
      <div class="container-fluid">
        <router-link class="navbar-brand" :to="{ name: 'doctorDashboard' }">
          {{ username }} Dashboard
        </router-link>

        <div class="collapse navbar-collapse">
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <router-link class="nav-link" :to="{ name: 'doctorProfile' }"> Profile </router-link>
            </li>
          </ul>

          <button class="btn btn-danger" @click="logout">Logout</button>
        </div>
      </div>
    </nav>

    <router-view />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = ref('')

const loadUsername = () => {
  username.value = localStorage.getItem('username') || 'User'
}

onMounted(() => {
  loadUsername()
  window.addEventListener('usernameUpdated', loadUsername)
})

const logout = () => {
  localStorage.clear()
  router.push({ name: 'auth' })
}
</script>
