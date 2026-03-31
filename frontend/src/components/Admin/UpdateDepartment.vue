<template>
  <div class="container mt-4">
    <h2>Update Department</h2>

    <input v-model="name" class="form-control mb-2" placeholder="Name" />

    <textarea v-model="description" class="form-control mb-3" placeholder="Description"></textarea>

    <h5>Doctors in this Department</h5>
    <div v-for="doc in currentDoctors" :key="doc.id">
      <input type="checkbox" :value="doc.id" v-model="selectedDoctors" />
      {{ doc.username }}
    </div>

    <h5 class="mt-3">Available Doctors</h5>
    <div v-for="doc in availableDoctors" :key="doc.id">
      <input type="checkbox" :value="doc.id" v-model="selectedDoctors" />
      {{ doc.username }}
    </div>

    <button class="btn btn-warning mt-3" @click="updateDept">Save</button>

    <button class="btn btn-outline-danger ms-2 mt-3" @click="goBack">Cancel</button>
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const name = ref('')
const description = ref('')

const currentDoctors = ref([])
const availableDoctors = ref([])
const selectedDoctors = ref([])

const token = localStorage.getItem('token')
const deptId = route.params.id

const fetchDept = async () => {
  const res = await axios.get('http://localhost:5000/admin_departments', {
    headers: { Authorization: `Bearer ${token}` },
  })

  const dept = res.data.departments.find((d) => d.id == deptId)

  if (dept) {
    name.value = dept.name
    description.value = dept.description

    currentDoctors.value = dept.doctors

    selectedDoctors.value = dept.doctors.map((d) => d.id)
  }

  availableDoctors.value = res.data.doctors
}

const updateDept = async () => {
  await axios.post(
    `http://localhost:5000/admin/update_department/${deptId}`,
    {
      name: name.value,
      description: description.value,
      doctor_ids: selectedDoctors.value,
    },
    {
      headers: { Authorization: `Bearer ${token}` },
    },
  )

  router.push({ name: 'adminDepartments' })
}

const goBack = () => {
  router.push({ name: 'adminDepartments' })
}

onMounted(fetchDept)
</script>
