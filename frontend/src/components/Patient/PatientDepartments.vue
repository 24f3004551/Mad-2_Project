<template>
  <div class="container mt-4">
    <h2>Departments</h2>

    <p v-if="loading">Loading...</p>

    <div v-else>
      <div v-if="departments.length">
        <div v-for="d in departments" :key="d.id">
          <h4>{{ d.name }}</h4>
          <p class="text-muted">{{ d.description }}</p>

          <div v-if="d.doctors.length">
            <table class="table table-striped">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Doctor</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>
                <tr v-for="(doc, i) in d.doctors" :key="doc.id">
                  <td>{{ i + 1 }}</td>
                  <td>{{ doc.username }}</td>

                  <td>
                    <button class="btn btn-warning" @click="checkSlots(doc.id)">Check Slots</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <p v-else class="text-secondary">No doctors assigned yet in this department.</p>

          <hr />
        </div>
      </div>

      <p v-else>No Departments</p>
    </div>
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const token = localStorage.getItem('token')

const departments = ref([])
const loading = ref(false)

const patientId = ref(null)

const fetchData = async () => {
  loading.value = true
  try {
    const res = await axios.get('http://localhost:5000/view_departments', {
      headers: { Authorization: 'Bearer ' + token },
    })

    departments.value = res.data.departments
    patientId.value = res.data.user_id
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const checkSlots = (doctorId) => {
  router.push({
    name: 'setupAppointment',
    params: {
      doctorId: doctorId,
      patientId: patientId.value,
    },
  })
}

onMounted(fetchData)
</script>
