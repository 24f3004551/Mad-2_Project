<template>
  <div class="container mt-3">
    <h2>Today's Appointments</h2>

    <table v-if="dailyAppointments.length" class="table">
      <tr v-for="(a, i) in dailyAppointments" :key="a.id">
        <td>{{ i + 1 }}</td>
        <td>{{ a.date }}</td>
        <td>{{ formatSlot(a.slot) }}</td>
        <td>{{ a.doctor || 'Doctor Deleted' }}</td>
        <td>{{ a.status }}</td>

        <td>
          <router-link v-if="a.has_treatment" :to="{ name: 'viewTreatment', params: { id: a.id } }">
            <button class="btn btn-warning">View Treatment</button>
          </router-link>

          <span v-else>None</span>
        </td>

        <td v-if="a.status === 'Booked'">
          <button class="btn btn-danger" @click="cancelAppointment(a.id)">Cancel</button>
        </td>
      </tr>
    </table>

    <p v-else>No appointments today</p>

    <h2 class="mt-4">All Appointments</h2>

    <table v-if="allAppointments.length" class="table">
      <tr v-for="(a, i) in allAppointments" :key="a.id">
        <td>{{ i + 1 }}</td>
        <td>{{ a.date }}</td>
        <td>{{ formatSlot(a.slot) }}</td>
        <td>{{ a.doctor || 'Doctor Deleted' }}</td>
        <td>{{ a.status }}</td>
        <td>
          <router-link v-if="a.has_treatment" :to="{ name: 'viewTreatment', params: { id: a.id } }">
            <button class="btn btn-warning">View</button>
          </router-link>
        </td>
      </tr>
    </table>

    <h2 class="mt-4">Book Appointment</h2>

    <input
      v-model="search"
      @input="fetchData"
      class="form-control w-25 my-2"
      placeholder="Search doctor / dept"
    />

    <table class="table" v-if="doctors.length">
      <tr v-for="(d, i) in doctors" :key="d.id">
        <td>{{ i + 1 }}</td>
        <td>{{ d.username }}</td>
        <td>{{ d.department }}</td>

        <td class="p-1">
          <button class="btn btn-warning" @click="checkSlots(d.id, patient_id)">Check Slots</button>
        </td>
      </tr>
    </table>
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const token = localStorage.getItem('token')
const router = useRouter()

const dailyAppointments = ref([])
const allAppointments = ref([])
const doctors = ref([])
const patient_id = ref()
const search = ref('')

const fetchData = async () => {
  const res = await axios.get('http://localhost:5000/patient_dashboard', {
    headers: { Authorization: `Bearer ${token}` },
    params: { q: search.value },
  })

  dailyAppointments.value = res.data.daily_appointments
  allAppointments.value = res.data.all_appointments
  doctors.value = res.data.doctors
  patient_id.value = res.data.user_id
}

const cancelAppointment = async (id) => {
  try {
    await axios.post(
      `http://localhost:5000/cancel_appointment/${id}`,
      {},
      {
        headers: { Authorization: `Bearer ${token}` },
      },
    )

    fetchData()
  } catch (err) {
    alert(err.response?.data?.error || 'Error')
  }
}

const checkSlots = (doctorId, patientId) => {
  router.push({
    name: 'setupAppointment',
    params: {
      doctorId: doctorId,
      patientId: patientId,
    },
  })
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
