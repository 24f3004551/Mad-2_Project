import { createRouter, createWebHistory } from 'vue-router'
import AuthView from '@/views/AuthView.vue'
import AdminView from '@/views/AdminView.vue'
import AdminDashboard from '@/components/Admin/AdminDashboard.vue'
import AdminDoctors from '@/components/Admin/AdminDoctors.vue'
import AdminDepartments from '@/components/Admin/AdminDepartments.vue'
import UpdateDepartment from '@/components/Admin/UpdateDepartment.vue'

const AdminPatients = { template: '<div class="p-3">Patients Page</div>' }
const AdminAppointments = { template: '<div class="p-3">Appointments Page</div>' }

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
      path: '/admin',
      name: 'admin',
      component: AdminView,
      meta: { role: 'admin' },
      children: [
        {
          path: '',
          name: 'AdminDashboard',
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
