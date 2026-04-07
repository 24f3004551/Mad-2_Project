<template>
  <div class="container mt-4">
    <h2>Appointments</h2>
    <p>Total no of appointments: {{ appointments.length }}</p>

    <table v-if="appointments.length" class="table table-striped">
      <thead>
        <tr>
          <th>#</th>
          <th>Date</th>
          <th>Time</th>
          <th>Patient</th>
          <th>Doctor</th>
          <th>Status</th>
          <th>Treatment</th>
          <th></th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="(a, i) in appointments" :key="a.id">
          <td>{{ i + 1 }}</td>
          <td>{{ formatDate(a.date) }}</td>
          <td>{{ formatSlot(a.slot) }}</td>
          <td>{{ a.patient }}</td>
          <td>{{ a.doctor || 'Doctor Deleted' }}</td>
          <td>{{ a.status }}</td>

          <td>
            <router-link
              v-if="a.has_treatment"
              :to="{ name: 'viewTreatment', params: { id: a.id } }"
            >
              <button class="btn btn-warning">View</button>
            </router-link>

            <span v-else>None</span>
          </td>

          <td>
            <button
              v-if="a.status === 'Booked'"
              class="btn btn-outline-danger"
              @click="cancelAppointment(a.id)"
            >
              Cancel
            </button>

            <button
              v-else-if="a.status === 'Cancelled'"
              class="btn btn-danger"
              @click="deleteAppointment(a.id)"
            >
              Delete
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <p v-else>No appointments found</p>
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref, onMounted } from 'vue'

const token = localStorage.getItem('token')
const appointments = ref([])

const fetchAppointments = async () => {
  const res = await axios.get('http://localhost:5000/admin_appointments', {
    headers: { Authorization: 'Bearer ' + token },
  })

  appointments.value = res.data.appointments
}

const cancelAppointment = async (id) => {
  await axios.post(
    `http://localhost:5000/cancel_appointment/${id}`,
    {},
    { headers: { Authorization: 'Bearer ' + token } },
  )

  fetchAppointments()
}

const deleteAppointment = async (id) => {
  if (!confirm('Delete this appointment?')) return

  await axios.post(
    `http://localhost:5000/admin/delete_appointment/${id}`,
    {},
    { headers: { Authorization: 'Bearer ' + token } },
  )

  fetchAppointments()
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString()
}

const formatSlot = (slot) => {
  const slot_time = {
    slot1: '8:00 AM - 9:00 AM',
    slot2: '9:00 AM - 10:00 AM',
    slot3: '10:00 AM - 11:00 AM',
    slot4: '1:00 PM - 2:00 PM',
    slot5: '2:00 PM - 3:00 PM',
    slot6: '3:00 PM - 4:00 PM',
  }
  return slot_time[slot] || slot
}

onMounted(fetchAppointments)
</script>
