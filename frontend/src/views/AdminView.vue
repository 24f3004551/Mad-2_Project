<template>
  <div>
    <div>
      <nav class="navbar navbar-expand-lg bg-warning">
        <div class="container-fluid">
          <router-link class="navbar-brand" :to="{ name: 'adminDashboard' }">
            Admin Dashboard
          </router-link>

          <div class="collapse navbar-collapse">
            <ul class="navbar-nav me-auto">
              <li class="nav-item">
                <router-link class="nav-link" :to="{ name: 'adminDoctors' }"> Doctors </router-link>
              </li>

              <li class="nav-item">
                <router-link class="nav-link" :to="{ name: 'adminPatients' }">
                  Patients
                </router-link>
              </li>

              <li class="nav-item">
                <router-link class="nav-link" :to="{ name: 'adminAppointments' }">
                  Appointments
                </router-link>
              </li>

              <li class="nav-item">
                <router-link class="nav-link" :to="{ name: 'adminDepartments' }">
                  Departments
                </router-link>
              </li>
            </ul>

            <button class="btn btn-danger" @click="logout">Logout</button>
          </div>
        </div>
      </nav>
    </div>
    <router-view />
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const logout = () => {
  localStorage.removeItem('token')
  router.push({ name: 'auth' })
}
</script>
