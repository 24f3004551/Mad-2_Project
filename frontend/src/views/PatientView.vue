<template>
  <div>
    <nav class="navbar navbar-expand-lg bg-warning">
      <div class="container-fluid">
        <router-link class="navbar-brand" :to="{ name: 'patientDashboard' }">
          {{ username }} Dashboard
        </router-link>

        <div class="collapse navbar-collapse">
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <router-link class="nav-link" :to="{ name: 'patientDashboard' }"> Home </router-link>
            </li>

            <li class="nav-item">
              <router-link class="nav-link" :to="{ name: 'patientProfile' }"> Profile </router-link>
            </li>

            <li class="nav-item">
              <router-link class="nav-link" :to="{ name: 'patientDepartments' }">
                Departments
              </router-link>
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
import { useRouter } from 'vue-router'

const router = useRouter()
const username = localStorage.getItem('username')

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('role')
  router.push({ name: 'auth' })
}
</script>
