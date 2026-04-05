<template>
  <div class="container mt-4">
    <h2>Doctor's Availability</h2>

    <div v-if="loading">Loading...</div>

    <div v-else>
      <div v-for="day in upcoming_days" :key="day" class="day-row">
        <div v-if="hasAnyVisibleSlot(day)">
          <div class="date-box">{{ formatDate(day) }}</div>

          <div class="d-flex flex-wrap">
            <label
              v-for="slot in getVisibleSlots(day)"
              :key="slot.key"
              class="slot-box"
              :class="getSlotClass(day, slot.key)"
            >
              <input
                type="checkbox"
                :checked="isChecked(day, slot.key)"
                @change="toggleSlot(day, slot.key)"
              />
              {{ slot.label }}
            </label>
          </div>
        </div>
      </div>

      <button class="btn btn-warning mt-3" @click="saveAvailability">Save</button>
    </div>
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const token = localStorage.getItem('token')

const router = useRouter()

const loading = ref(false)
const upcoming_days = ref([])
const availability = ref({})
const today = ref('')
const currentHour = ref(0)

const slots = [
  { key: 'slot1', label: '8:00 AM - 9:00 AM', hour: 8 },
  { key: 'slot2', label: '9:00 AM - 10:00 AM', hour: 9 },
  { key: 'slot3', label: '10:00 AM - 11:00 AM', hour: 10 },
  { key: 'slot4', label: '1:00 PM - 2:00 PM', hour: 13 },
  { key: 'slot5', label: '2:00 PM - 3:00 PM', hour: 14 },
  { key: 'slot6', label: '3:00 PM - 4:00 PM', hour: 15 },
]

const fetchAvailability = async () => {
  loading.value = true
  try {
    const res = await axios.get('http://localhost:5000/doctor_availability', {
      headers: { Authorization: 'Bearer ' + token },
    })

    upcoming_days.value = res.data.upcoming_days
    availability.value = res.data.availability
    today.value = res.data.today
    currentHour.value = res.data.current_hour
    console.log('current hour: ', currentHour)
    console.log('today: ', today)
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const isSlotVisible = (day, slotKey) => {
  const slot = slots.find((s) => s.key === slotKey)

  if (day !== today.value) {
    return true
  }

  if (currentHour.value > slot.hour) {
    return false
  }

  return true
}

const hasAnyVisibleSlot = (day) => {
  for (const slot of slots) {
    if (isSlotVisible(day, slot.key)) {
      return true
    }
  }

  return false
}

const getVisibleSlots = (day) => {
  const visible = []

  for (const slot of slots) {
    if (isSlotVisible(day, slot.key)) {
      visible.push(slot)
    }
  }

  return visible
}

const toggleSlot = (day, slot) => {
  const key = `${day}_${slot}`

  if (availability.value[key] == undefined) {
    availability.value[key] = {
      available: true,
    }
  } else {
    if (availability.value[key].available == true) {
      availability.value[key].available = false
    } else {
      availability.value[key].available = true
    }
  }
}

const isChecked = (day, slot) => {
  const key = `${day}_${slot}`

  if (availability.value[key] == undefined) {
    return false
  }

  if (availability.value[key].available == true) {
    return true
  } else {
    return false
  }
}

const getSlotClass = (day, slot) => {
  const key = `${day}_${slot}`
  const data = availability.value[key]

  if (!data) return 'unavailable'
  if (data.booked) return 'booked'
  if (data.available) return 'available'
  return 'unavailable'
}

const saveAvailability = async () => {
  await axios.post(
    'http://localhost:5000/doctor_availability',
    { availability: availability.value },
    { headers: { Authorization: 'Bearer ' + token } },
  )

  alert('Saved!')
  router.push({ name: 'doctorDashboard' })
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString()
}

onMounted(fetchAvailability)
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

.booked {
  border-color: blue;
  color: blue;
}

.unavailable {
  border-color: red;
  color: red;
}

.date-box {
  font-weight: bold;
  margin-bottom: 5px;
}
</style>
