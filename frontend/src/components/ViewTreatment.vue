<template>
  <div class="container mt-4">
    <h2>Treatment for {{ patientName }}</h2>

    <div class="mb-3">
      <div>{{ date }}</div>
      <div>Patient: {{ patientName }}</div>
      <div>Doctor: {{ doctorName }}</div>
    </div>

    <hr />

    <div class="mb-3">
      <h4>Diagnosis</h4>
      <p>{{ diagnosis }}</p>
    </div>

    <div v-if="prescription" class="mb-3">
      <h4>Prescription</h4>
      <p>{{ prescription }}</p>
    </div>

    <div v-if="notes" class="mb-3">
      <h4>Notes</h4>
      <p>{{ notes }}</p>
    </div>

    <button class="btn btn-outline-danger" @click="goBack">Go Back</button>

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

const apptId = route.params.id
const token = localStorage.getItem('token')

const diagnosis = ref('')
const prescription = ref('')
const notes = ref('')
const patientName = ref('')
const doctorName = ref('')
const date = ref('')
const pastHistory = ref([])

const fetchData = async () => {
  try {
    const res = await axios.get(`http://localhost:5000/view_treatment/${apptId}`, {
      headers: { Authorization: 'Bearer ' + token },
    })

    diagnosis.value = res.data.diagnosis
    prescription.value = res.data.prescription
    notes.value = res.data.notes
    patientName.value = res.data.patient
    doctorName.value = res.data.doctor
    date.value = res.data.date
    pastHistory.value = res.data.history
  } catch (err) {
    console.error(err)
  }
}

const goBack = () => {
  router.back()
}

onMounted(fetchData)
</script>
