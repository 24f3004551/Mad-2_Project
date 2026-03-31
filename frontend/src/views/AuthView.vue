<template>
  <div class="container w-50 d-flex flex-column justify-content-center vh-100">
    <h2>{{ isLogin ? 'Login' : 'Signup' }}</h2>

    <input v-model="username" placeholder="Username" class="form-control my-2" />
    <input v-model="password" type="password" placeholder="Password" class="form-control my-2" />

    <button @click="handleAuth" class="btn btn-warning">
      {{ isLogin ? 'Login' : 'Signup' }}
    </button>

    <p class="mt-3">
      <span class="me-2" v-if="isLogin">New user?</span>
      <span class="me-2" v-else>Already have account?</span>
      <a href="#" @click="isLogin = !isLogin">
        {{ isLogin ? 'Signup' : 'Login' }}
      </a>
    </p>

    <p v-if="error" class="text-danger">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const username = ref('')
const password = ref('')
const isLogin = ref(true)
const error = ref('')

const router = useRouter()

const handleAuth = async () => {
  try {
    const url = isLogin.value ? 'http://localhost:5000/login' : 'http://localhost:5000/signup'

    const res = await axios.post(url, {
      username: username.value,
      password: password.value,
    })

    localStorage.setItem('token', res.data.token)
    localStorage.setItem('username', res.data.user.username)
    localStorage.setItem('role', res.data.user.role)

    router.push('/')
  } catch (err) {
    console.log(err)
    error.value = err.response.data.error || 'Something went wrong'
    username.value = ''
    password.value = ''
  }
}
</script>
