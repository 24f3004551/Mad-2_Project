import { createRouter, createWebHistory } from 'vue-router'
import AuthView from '@/views/AuthView.vue'
import AdminView from '@/views/AdminView.vue'
import AdminDashboard from '@/components/Admin/AdminDashboard.vue'
import AdminDoctors from '@/components/Admin/AdminDoctors.vue'
import AdminDepartments from '@/components/Admin/AdminDepartments.vue'
import UpdateDepartment from '@/components/Admin/UpdateDepartment.vue'
import DoctorView from '@/views/DoctorView.vue'
import DoctorDashboard from '@/components/Doctor/DoctorDashboard.vue'
import PatientDashboard from '@/components/Patient/PatientDashboard.vue'
import PatientView from '@/views/PatientView.vue'

const AdminPatients = { template: '<div class="p-3">Patients Page</div>' }
const AdminAppointments = { template: '<div class="p-3">Appointments Page</div>' }
const PatientProfile = { template: '<div class="p-3">Profile Page</div>' }
const PatientDepartments = { template: '<div class="p-3">Departments Page</div>' }

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'base',
      redirect: () => {
        const role = localStorage.getItem('role')
        if (role === 'admin') return '/admin'
        if (role === 'doctor') return '/doctor'
        if (role === 'patient') return '/patient'
        return '/auth'
      },
    },
    {
      path: '/auth',
      name: 'auth',
      component: AuthView,
    },
    {
      path: '/patient',
      name: 'patient',
      component: PatientView,
      meta: { role: 'patient' },
      children: [
        {
          path: '',
          name: 'patientDashboard',
          component: PatientDashboard,
        },
        {
          path: 'profile',
          name: 'patientProfile',
          component: PatientProfile,
        },
        {
          path: 'departments',
          name: 'patientDepartments',
          component: PatientDepartments,
        },
      ],
    },
    {
      path: '/doctor',
      name: 'doctor',
      component: DoctorView,
      meta: { role: 'doctor' },
      children: [
        {
          path: '',
          name: 'doctorDashboard',
          component: DoctorDashboard,
        },
      ],
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminView,
      meta: { role: 'admin' },
      children: [
        {
          path: '',
          name: 'adminDashboard',
          component: AdminDashboard,
        },
        {
          path: 'doctors',
          name: 'adminDoctors',
          component: AdminDoctors,
        },
        {
          path: 'patients',
          name: 'adminPatients',
          component: AdminPatients,
        },
        {
          path: 'appointments',
          name: 'adminAppointments',
          component: AdminAppointments,
        },
        {
          path: 'departments',
          name: 'adminDepartments',
          component: AdminDepartments,
        },
        {
          path: 'departments/update/:id',
          name: 'updateDepartment',
          component: UpdateDepartment,
        },
      ],
    },
  ],
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')

  if (to.name !== 'auth' && !token) {
    return next({ name: 'auth' })
  }

  if (to.meta?.role && to.meta.role !== role) {
    return next({ name: 'auth' })
  }

  if (to.name == 'auth' && token) {
    return next({ name: 'base' })
  }

  next()
})

export default router
