<template>
  <div>
    <div v-if="error" class="text-center mt-5 text-danger">
      <h3>{{ error }}</h3>
    </div>
    <div v-else class="container mt-4">
      <div class="card p-3 my-2 bg-success">
        <h3>Doctors</h3>
        <p>Total: {{ doctors.length }}</p>
      </div>

      <div class="card p-3 my-2 bg-warning">
        <h3>Patients</h3>
        <p>Total: {{ patients.length }}</p>
      </div>

      <div class="card p-3 my-2 bg-primary">
        <h3>Appointments</h3>
        <p>Total: {{ appointments.length }}</p>
      </div>

      <div class="card p-3 my-2 bg-danger">
        <h3>Departments</h3>
        <p>Total: {{ departments.length }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const error = ref('')
const doctors = ref([])
const patients = ref([])
const departments = ref([])
const appointments = ref([])

onMounted(async () => {
  try {
    const token = localStorage.getItem('token')

    const res = await axios.get('http://localhost:5000/admin_dashboard', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    console.log('This is my data: ', res.data)

    doctors.value = res.data.doctors || []
    patients.value = res.data.patients || []
    departments.value = res.data.departments || []
    appointments.value = res.data.appointments || []
  } catch (err) {
    error.value = err.response.data.error || 'Something went wrong'

    console.log(err)
  }
})
</script>
