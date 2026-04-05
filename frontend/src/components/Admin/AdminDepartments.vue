<template>
  <div class="container mt-4">
    <h2>Departments</h2>
    <p>Total no of Departments: {{ departments.length }}</p>

    <table class="table" v-if="departments.length">
      <thead>
        <tr>
          <th>#</th>
          <th>Name</th>
          <th>Description</th>
          <th></th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="(dept, index) in departments" :key="dept.id">
          <td>{{ index + 1 }}</td>
          <td>{{ dept.name }}</td>
          <td>{{ dept.description }}</td>
          <td class="d-flex">
            <button class="btn btn-outline-success mx-2" @click="goToUpdate(dept.id)">
              Update
            </button>

            <button class="btn btn-outline-danger" @click="deleteDept(dept.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>

    <div class="mt-5">
      <h2>Add Department</h2>

      <input v-model="dept_name" class="form-control mb-2" placeholder="Name" />
      <input v-model="description" class="form-control mb-2" placeholder="Description" />

      <label class="my-2">Assign Doctors</label>

      <div v-for="doc in doctors" :key="doc.id">
        <input type="checkbox" :value="doc.id" v-model="selectedDoctors" />
        {{ doc.username }}
      </div>

      <button class="btn btn-warning mt-3" @click="addDept">Add Department</button>
    </div>
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const departments = ref([])
const doctors = ref([])

const dept_name = ref('')
const description = ref('')
const selectedDoctors = ref([])

const token = localStorage.getItem('token')

const fetchData = async () => {
  const res = await axios.get('http://localhost:5000/admin_departments', {
    headers: { Authorization: `Bearer ${token}` },
  })

  departments.value = res.data.departments
  doctors.value = res.data.doctors
}

const addDept = async () => {
  await axios.post(
    'http://localhost:5000/admin/add_department',
    {
      dept_name: dept_name.value,
      description: description.value,
      doctor_ids: selectedDoctors.value,
    },
    {
      headers: { Authorization: `Bearer ${token}` },
    },
  )
  dept_name.value = ''
  description.value = ''
  selectedDoctors.value = []

  fetchData()
}

const deleteDept = async (id) => {
  await axios.post(
    `http://localhost:5000/admin/delete_department/${id}`,
    {},
    {
      headers: { Authorization: `Bearer ${token}` },
    },
  )

  fetchData()
}

const goToUpdate = (id) => {
  router.push({ name: 'updateDepartment', params: { id } })
}

onMounted(fetchData)
</script>
