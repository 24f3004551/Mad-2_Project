<template>
  <div class="container mt-4">
    <h2>Edit Doctor</h2>

    <input v-model="username" class="form-control my-2" placeholder="Username" />

    <input
      v-model="password"
      type="password"
      class="form-control my-2"
      placeholder="New Password (optional)"
    />

    <select v-model="department_id" class="form-select my-2">
      <option value="null">Select Department</option>
      <option v-for="d in departments" :key="d.id" :value="d.id">
        {{ d.name }}
      </option>
    </select>

    <button class="btn btn-success" @click="updateDoctor">Update</button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRoute } from 'vue-router'

const route = useRoute()
const doctorId = route.params.id

const username = ref('')
const password = ref('')
const department_id = ref('')
const departments = ref([])

const token = localStorage.getItem('token')

const fetchDoctor = async () => {
  const res = await axios.get(`http://localhost:5000/admin/get_doctor/${doctorId}`, {
    headers: { Authorization: `Bearer ${token}` },
  })

  username.value = res.data.username
  department_id.value = res.data.department_id
  departments.value = res.data.departments
}

const updateDoctor = async () => {
  await axios.put(
    `http://localhost:5000/admin/update_doctor/${doctorId}`,
    {
      username: username.value,
      password: password.value,
      department_id: department_id.value,
    },
    { headers: { Authorization: `Bearer ${token}` } },
  )

  alert('Doctor updated')
}

onMounted(fetchDoctor)
</script>
