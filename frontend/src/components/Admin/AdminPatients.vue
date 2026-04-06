<template>
  <div class="container mt-4">
    <h2>Patients</h2>
    <p>Total no of patients: {{ patients.length }}</p>

    <input
      v-if="totalPatients > 0"
      v-model="search"
      @input="fetchPatients"
      class="form-control w-25 my-2"
      placeholder="Search"
    />

    <table v-if="patients.length" class="table table-striped">
      <thead>
        <tr>
          <th>#</th>
          <th>Username</th>
          <th></th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="(p, i) in patients" :key="p.id">
          <td>{{ i + 1 }}</td>
          <td>{{ p.username }}</td>

          <td class="d-flex">
            <button class="btn btn-warning mx-2" @click="toggleBlacklist(p.id)">
              {{ p.blacklist ? 'UnBlacklist' : 'Blacklist' }}
            </button>

            <button class="btn btn-outline-danger" @click="deletePatient(p.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>

    <p v-if="!patients.length && totalPatients > 0">No matching patients found</p>

    <p v-if="totalPatients === 0">No patients available</p>
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref, onMounted } from 'vue'

const token = localStorage.getItem('token')

const patients = ref([])
const totalPatients = ref(0)
const search = ref('')

const fetchPatients = async () => {
  const res = await axios.get('http://localhost:5000/admin_patients', {
    headers: { Authorization: 'Bearer ' + token },
    params: { q: search.value },
  })

  patients.value = res.data.patients
  totalPatients.value = res.data.total_patients
}

const toggleBlacklist = async (id) => {
  await axios.post(
    `http://localhost:5000/admin/blacklist_user/${id}`,
    {},
    { headers: { Authorization: 'Bearer ' + token } },
  )

  fetchPatients()
}

const deletePatient = async (id) => {
  if (!confirm('Are you sure you want to delete this patient?')) return

  await axios.post(
    `http://localhost:5000/admin/delete_patient/${id}`,
    {},
    { headers: { Authorization: 'Bearer ' + token } },
  )

  fetchPatients()
}

onMounted(fetchPatients)
</script>
