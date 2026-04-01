<template>
  <div>
    <nav class="navbar navbar-expand-lg bg-warning">
      <div class="container-fluid">
        <router-link class="navbar-brand" :to="{ name: 'doctorDashboard' }">
          {{ doctor?.username }} Dashboard
        </router-link>

        <button class="btn btn-danger" @click="logout">Logout</button>
      </div>
    </nav>

    <router-view />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const doctor = ref(JSON.parse(localStorage.getItem('user') || '{}'))

const logout = () => {
  localStorage.clear()
  router.push({ name: 'auth' })
}
</script>
