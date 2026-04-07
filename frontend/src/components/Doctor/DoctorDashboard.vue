<template>
  <div class="container mt-3">
    <h2>Today's Pending Appointments</h2>

    <p v-if="loading">Loading...</p>

    <table v-else-if="dailyAppointments.length" class="table">
      <tr v-for="(a, i) in dailyAppointments" :key="a.id">
        <td class="p-2">{{ i + 1 }}</td>
        <td class="p-2">{{ a.date }}</td>
        <td class="p-2">{{ formatSlot(a.slot) }}</td>
        <td class="p-2">{{ a.patient }}</td>
        <td class="p-2">{{ a.status }}</td>

        <td v-if="a.has_treatment" class="p-2">
          <router-link :to="{ name: 'treatment', params: { appointmentId: a.id } }"
            ><button class="btn btn-warning">View Treatment</button></router-link
          >
        </td>
        <td v-else class="p-2">
          <router-link :to="{ name: 'treatment', params: { appointmentId: a.id } }"
            ><button class="btn btn-outline-success">Treat</button></router-link
          >
        </td>
      </tr>
    </table>

    <p v-else>No Appointment for today!!!</p>

    <h2>Assigned Patients</h2>
    <table v-if="patients.length" class="table">
      <tr v-for="(p, i) in patients" :key="p.id">
        <td>{{ i + 1 }}</td>
        <td>{{ p.username }}</td>
      </tr>
    </table>

    <p v-else>No assigned patients yet.</p>

    <h2>All Appointments</h2>
    <table v-if="allAppointments.length" class="table">
      <tr v-for="(a, i) in allAppointments" :key="a.id">
        <td class="p-2">{{ i + 1 }}</td>
        <td class="p-2">{{ a.date }}</td>
        <td class="p-2">{{ formatSlot(a.slot) }}</td>
        <td class="p-2">{{ a.patient }}</td>
        <td class="p-2">{{ a.status }}</td>
        <td class="p-2">
          <router-link
            v-if="a.status === 'Finished' && a.has_treatment"
            :to="{ name: 'treatment', params: { appointmentId: a.id } }"
          >
            <button class="btn btn-warning">View</button>
          </router-link>

          <router-link
            v-else-if="a.status === 'Booked' && !a.has_treatment"
            :to="{ name: 'treatment', params: { appointmentId: a.id } }"
          >
            <button class="btn btn-outline-success">Treat</button>
          </router-link>
        </td>

        <td v-if="a.status === 'Booked'" class="p-2">
          <button class="btn btn-danger" @click="cancelAppointment(a.id)">Cancel</button>
        </td>
      </tr>
    </table>

    <router-link :to="{ name: 'doctorAvailability' }">
      <button class="btn btn-warning mt-3">Update Availability</button>
    </router-link>
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref, onMounted } from 'vue'

const dailyAppointments = ref([])
const patients = ref([])
const allAppointments = ref([])
const loading = ref(false)

const token = localStorage.getItem('token')

const fetchData = async () => {
  if (!token) {
    console.error('No token found')
    return
  }

  try {
    loading.value = true

    const res = await axios.get('http://localhost:5000/doctor_dashboard', {
      headers: {
        Authorization: 'Bearer ' + token,
      },
    })

    dailyAppointments.value = res.data.daily_appointments
    patients.value = res.data.assigned_patients
    allAppointments.value = res.data.all_appointments
  } catch (err) {
    console.error(err.response?.data || err.message)
  } finally {
    loading.value = false
  }
}

const cancelAppointment = async (id) => {
  try {
    await axios.post(
      `http://localhost:5000/cancel_appointment/${id}`,
      {},
      {
        headers: { Authorization: 'Bearer ' + token },
      },
    )

    fetchData()
  } catch (err) {
    alert(err.response?.data?.error || 'Error')
  }
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

onMounted(fetchData)
</script>
