<template>
  <div class="container mt-4 mb-3">
    <h2>Doctors</h2>

    <input
      v-model="search"
      @input="fetchDoctors"
      class="form-control w-25 my-2"
      placeholder="Search..."
    />

    <table class="table table-striped" v-if="doctors.length">
      <thead>
        <tr>
          <th>#</th>
          <th>Username</th>
          <th>Department</th>
          <th>Actions</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="(doc, index) in doctors" :key="doc.id">
          <td>{{ index + 1 }}</td>
          <td>{{ doc.username }}</td>
          <td>{{ doc.department || 'Unassigned' }}</td>
          <td>
            <button class="btn btn-primary mx-1" @click="goToEdit(doc.id)">Edit</button>
          </td>

          <td>
            <button class="btn btn-warning mx-1" @click="toggleBlacklist(doc)">
              {{ doc.blacklist ? 'Unblacklist' : 'Blacklist' }}
            </button>

            <button class="btn btn-danger mx-1" @click="deleteDoctor(doc.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>

    <h3 class="mt-4">Add Doctor</h3>

    <input v-model="newUsername" placeholder="Username" class="form-control my-2" />
    <input v-model="newPassword" placeholder="Password" type="password" class="form-control my-2" />

    <select v-model="selectedDept" class="form-select my-2">
      <option value="">Select Department</option>
      <option v-for="d in departments" :key="d.id" :value="d.id">
        {{ d.name }}
      </option>
    </select>

    <button class="btn btn-warning" @click="addDoctor">Add</button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()

const doctors = ref([])
const departments = ref([])
const search = ref('')

const newUsername = ref('')
const newPassword = ref('')
const selectedDept = ref('')

const token = localStorage.getItem('token')

const fetchDoctors = async () => {
  const res = await axios.get('http://localhost:5000/admin_doctors', {
    headers: { Authorization: `Bearer ${token}` },
    params: { q: search.value },
  })

  doctors.value = res.data.doctors
  departments.value = res.data.departments
}

const addDoctor = async () => {
  await axios.post(
    'http://localhost:5000/admin/add_doctor',
    {
      username: newUsername.value,
      password: newPassword.value,
      department_id: selectedDept.value,
    },
    { headers: { Authorization: `Bearer ${token}` } },
  )

  fetchDoctors()
}

const deleteDoctor = async (id) => {
  if (!confirm('Are you sure you want to delete this doctor?')) return

  try {
    const token = localStorage.getItem('token')

    const res = await axios.delete(`http://localhost:5000/admin/delete_doctor/${id}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    alert(res.data.message)
    fetchDoctors()
  } catch (err) {
    console.error(err)
    alert(err.response?.data?.error || 'Something went wrong')
  }
}

const goToEdit = (id) => {
  router.push(`/admin/edit-doctor/${id}`)
}

const toggleBlacklist = async (doc) => {
  await axios.post(
    `http://localhost:5000/admin/blacklist_user/${doc.id}`,
    {},
    {
      headers: { Authorization: `Bearer ${token}` },
    },
  )

  fetchDoctors()
}

onMounted(fetchDoctors)
</script>
