<template>
  <div class="container mt-4">
    <h2>Treatment for {{ patientName }}</h2>

    <form class="w-50" @submit.prevent="saveTreatment">
      <div class="mb-3">
        <label>Diagnosis</label>
        <textarea v-model="diagnosis" class="form-control"></textarea>
      </div>

      <div class="mb-3">
        <label>Prescription</label>
        <textarea v-model="prescription" class="form-control"></textarea>
      </div>

      <div class="mb-3">
        <label>Notes</label>
        <textarea v-model="notes" class="form-control"></textarea>
      </div>

      <button class="btn btn-warning">Save</button>
      <button type="button" class="btn btn-outline-danger ms-2" @click="goBack">Cancel</button>
    </form>

    <h2 class="mt-4">Past History</h2>

    <div v-if="pastHistory.length" class="d-flex flex-wrap gap-3">
      <div v-for="p in pastHistory" :key="p.id" class="card p-3" style="width: 300px">
        <h5>{{ p.date }}</h5>
        <p><strong>Diagnosis:</strong> {{ p.diagnosis }}</p>
        <p v-if="p.prescription"><strong>Prescription:</strong> {{ p.prescription }}</p>
        <p v-if="p.notes"><strong>Notes:</strong> {{ p.notes }}</p>
      </div>
    </div>

    <p v-else>No Past History</p>
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const apptId = route.params.appointmentId
const token = localStorage.getItem('token')

const diagnosis = ref('')
const prescription = ref('')
const notes = ref('')
const patientName = ref('')
const pastHistory = ref([])

const fetchData = async () => {
  try {
    const res = await axios.get(`http://localhost:5000/treatment/${apptId}`, {
      headers: { Authorization: 'Bearer ' + token },
    })

    diagnosis.value = res.data.diagnosis
    prescription.value = res.data.prescription
    notes.value = res.data.notes
    patientName.value = res.data.patient
    pastHistory.value = res.data.history
  } catch (err) {
    console.error(err)
    alert('Failed to load data')
  }
}

const saveTreatment = async () => {
  await axios.post(
    `http://localhost:5000/treatment/${apptId}`,
    {
      diagnosis: diagnosis.value,
      prescription: prescription.value,
      notes: notes.value,
    },
    { headers: { Authorization: 'Bearer ' + token } },
  )

  alert('Treatment saved!')
  router.push('/doctor')
}

const goBack = () => {
  router.push('/doctor')
}

onMounted(fetchData)
</script>
