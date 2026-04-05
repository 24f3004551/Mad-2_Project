<template>
  <div class="container mt-4">
    <h2>Doctor's Upcoming Availability</h2>

    <div v-if="loading">Loading...</div>

    <div v-else>
      <div v-if="Object.keys(grouped).length">
        <div v-for="(slotsData, day) in grouped" :key="day">
          <div v-if="isDayVisible(day)">
            <div class="date-box">{{ formatDate(day) }}</div>

            <div class="d-flex flex-wrap">
              <label
                v-for="s in getVisibleSlots(day)"
                :key="s.key"
                class="slot-box"
                :class="getSlotClass(day, s.key)"
              >
                <input
                  type="radio"
                  name="selected_slot"
                  :value="day + '|' + s.key"
                  v-model="selectedSlot"
                />
                {{ s.label }}
              </label>
            </div>
          </div>
        </div>

        <button class="btn btn-warning mt-3" @click="bookAppointment">Book</button>
      </div>

      <p v-else>No availability for this doctor</p>
    </div>
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const token = localStorage.getItem('token')

const patientId = route.params.patientId
const doctorId = route.params.doctorId

const loading = ref(false)
const grouped = ref({})
const today = ref('')
const currentHour = ref(0)

const selectedSlot = ref('')

const slots = [
  { key: 'slot1', label: '8:00 AM - 9:00 AM', hour: 8 },
  { key: 'slot2', label: '9:00 AM - 10:00 AM', hour: 9 },
  { key: 'slot3', label: '10:00 AM - 11:00 AM', hour: 10 },
  { key: 'slot4', label: '1:00 PM - 2:00 PM', hour: 13 },
  { key: 'slot5', label: '2:00 PM - 3:00 PM', hour: 14 },
  { key: 'slot6', label: '3:00 PM - 4:00 PM', hour: 15 },
]

const fetchData = async () => {
  loading.value = true
  try {
    const res = await axios.get(
      `http://localhost:5000/setup_appointment/${patientId}/${doctorId}`,
      { headers: { Authorization: 'Bearer ' + token } },
    )

    grouped.value = res.data.grouped
    today.value = res.data.today
    currentHour.value = res.data.current_hour
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const isDayVisible = (day) => {
  if (day > today.value) return true

  if (day === today.value && currentHour.value < 15) return true

  return false
}

const isSlotVisible = (day, hour) => {
  if (day > today.value) return true

  if (day === today.value && currentHour.value < hour) return true

  return false
}

const getVisibleSlots = (day) => {
  const visible = []

  for (const slot of slots) {
    if (isSlotVisible(day, slot.hour)) {
      visible.push(slot)
    }
  }

  return visible
}

const getSlotClass = (day, slotKey) => {
  if (grouped.value[day] && grouped.value[day][slotKey]) {
    return 'available'
  }
  return 'no-slot'
}

const bookAppointment = async () => {
  if (!selectedSlot.value) {
    alert('Select a slot')
    return
  }

  try {
    await axios.post(
      `http://localhost:5000/setup_appointment/${patientId}/${doctorId}`,
      { selected_slot: selectedSlot.value },
      { headers: { Authorization: 'Bearer ' + token } },
    )

    alert('Appointment booked!')

    router.push({ name: 'patientDashboard' })
  } catch (err) {
    alert(err.response?.data?.error || 'Error')
  }
}

const formatDate = (d) => {
  return new Date(d).toLocaleDateString()
}

onMounted(fetchData)
</script>

<style>
.slot-box {
  padding: 10px;
  margin: 5px;
  border: 2px solid;
  cursor: pointer;
}

.available {
  border-color: green;
  color: green;
}

.no-slot {
  border-color: red;
  color: red;
}

.date-box {
  font-weight: bold;
  margin-bottom: 5px;
}
</style>
