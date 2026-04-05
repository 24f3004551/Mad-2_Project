<template>
  <div class="container mt-4 w-50">
    <h2>{{ username }} Profile</h2>

    <div v-if="message" class="alert" :class="alertClass">
      {{ message }}
    </div>

    <form @submit.prevent="updateProfile">
      <div class="mb-3">
        <label>Username</label>
        <input v-model="username" class="form-control" />

        <label class="mt-2">Password</label>
        <input v-model="password" type="password" class="form-control" />
      </div>

      <button class="btn btn-warning">Submit</button>
    </form>
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref, onMounted } from 'vue'

const token = localStorage.getItem('token')

const username = ref('')
const password = ref('')

const message = ref('')
const alertClass = ref('alert-success')

const fetchProfile = async () => {
  const res = await axios.get('http://localhost:5000/profile', {
    headers: { Authorization: 'Bearer ' + token },
  })

  username.value = res.data.username
}

const updateProfile = async () => {
  try {
    const res = await axios.post(
      'http://localhost:5000/profile',
      {
        username: username.value,
        password: password.value,
      },
      {
        headers: { Authorization: 'Bearer ' + token },
      },
    )

    localStorage.setItem('username', username.value)
    window.dispatchEvent(new Event('usernameUpdated'))

    message.value = res.data.msg
    alertClass.value = 'alert-success'

    password.value = ''
  } catch (err) {
    message.value = err.response?.data?.error || 'Error'
    alertClass.value = 'alert-danger'
  }

  setTimeout(() => {
    message.value = ''
  }, 2000)
}

onMounted(fetchProfile)
</script>
