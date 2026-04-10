<template>
  <AppLayout>
    <template #default>
      <h1 class="page-title mb-3">Настройки</h1>

      <div class="tabs">
        <button :class="['tab-btn', activeTab === 'org' && 'active']" @click="activeTab = 'org'">Организация</button>
        <button :class="['tab-btn', activeTab === 'users' && 'active']" @click="activeTab = 'users'">Пользователи</button>
        <button :class="['tab-btn', activeTab === 'projects' && 'active']" @click="activeTab = 'projects'">Проекты</button>
      </div>

      <!-- ORG TAB -->
      <div v-if="activeTab === 'org'">
        <div class="tabs tabs-inner">
          <button :class="['tab-btn', orgTab === 'ooo' && 'active']" @click="orgTab = 'ooo'">ООО</button>
          <button :class="['tab-btn', orgTab === 'ip' && 'active']" @click="orgTab = 'ip'">ИП</button>
          <button :class="['tab-btn', orgTab === 'files' && 'active']" @click="orgTab = 'files'">Файлы</button>
        </div>

        <!-- ООО -->
        <div v-if="orgTab === 'ooo'" class="card" style="max-width: 640px;">
          <form @submit.prevent="saveOrg">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0 16px;">
              <div class="form-group">
                <label>Полное название</label>
                <input v-model="orgForm.name" type="text" />
              </div>
              <div class="form-group">
                <label>Краткое название</label>
                <input v-model="orgForm.short_name" type="text" />
              </div>
              <div class="form-group">
                <label>ИНН</label>
                <input v-model="orgForm.inn" type="text" />
              </div>
              <div class="form-group">
                <label>ОГРН</label>
                <input v-model="orgForm.ogrn" type="text" />
              </div>
              <div class="form-group" style="grid-column: 1 / -1;">
                <label>Юридический адрес</label>
                <input v-model="orgForm.legal_address" type="text" />
              </div>
              <div class="form-group" style="grid-column: 1 / -1;">
                <label>Банк</label>
                <input v-model="orgForm.bank_name" type="text" />
              </div>
              <div class="form-group">
                <label>БИК</label>
                <input v-model="orgForm.bik" type="text" />
              </div>
              <div class="form-group">
                <label>Р/счёт</label>
                <input v-model="orgForm.account" type="text" />
              </div>
              <div class="form-group">
                <label>Корр. счёт</label>
                <input v-model="orgForm.corr_account" type="text" />
              </div>
              <div class="form-group">
                <label>Телефон</label>
                <input v-model="orgForm.phone" type="text" />
              </div>
              <div class="form-group">
                <label>ФИО подписанта</label>
                <input v-model="orgForm.signer_name" type="text" placeholder="Дьяченко О.Н." />
              </div>
              <div class="form-group">
                <label>Должность подписанта</label>
                <input v-model="orgForm.signer_role" type="text" placeholder="Директор" />
              </div>
            </div>
            <p v-if="orgSaved" style="color: var(--color-success); font-size: 0.875rem;">Сохранено ✓</p>
            <button type="submit" class="btn btn-primary">Сохранить</button>
          </form>
        </div>

        <!-- ИП -->
        <div v-if="orgTab === 'ip'" class="card" style="max-width: 640px;">
          <form @submit.prevent="saveOrg">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0 16px;">
              <div class="form-group" style="grid-column: 1 / -1;">
                <label>ФИО ИП (полное)</label>
                <input v-model="orgForm.ip_full_name" type="text" placeholder="Иванов Иван Иванович" />
              </div>
              <div class="form-group">
                <label>ИНН</label>
                <input v-model="orgForm.ip_inn" type="text" />
              </div>
              <div class="form-group">
                <label>ОГРНИП</label>
                <input v-model="orgForm.ip_ogrnip" type="text" />
              </div>
              <div class="form-group" style="grid-column: 1 / -1;">
                <label>Юридический адрес</label>
                <input v-model="orgForm.ip_legal_address" type="text" />
              </div>
              <div class="form-group" style="grid-column: 1 / -1;">
                <label>Банк</label>
                <input v-model="orgForm.ip_bank_name" type="text" />
              </div>
              <div class="form-group">
                <label>БИК</label>
                <input v-model="orgForm.ip_bik" type="text" />
              </div>
              <div class="form-group">
                <label>Р/счёт</label>
                <input v-model="orgForm.ip_account" type="text" />
              </div>
              <div class="form-group">
                <label>Корр. счёт</label>
                <input v-model="orgForm.ip_corr_account" type="text" />
              </div>
              <div class="form-group">
                <label>Телефон</label>
                <input v-model="orgForm.ip_phone" type="text" />
              </div>
              <div class="form-group">
                <label>ФИО подписанта</label>
                <input v-model="orgForm.ip_signer_name" type="text" placeholder="Иванов И.И." />
              </div>
              <div class="form-group">
                <label>Должность подписанта</label>
                <input v-model="orgForm.ip_signer_role" type="text" placeholder="Индивидуальный предприниматель" />
              </div>
            </div>
            <p v-if="orgSaved" style="color: var(--color-success); font-size: 0.875rem;">Сохранено ✓</p>
            <button type="submit" class="btn btn-primary">Сохранить</button>
          </form>
        </div>

        <!-- Файлы -->
        <div v-if="orgTab === 'files'" class="card" style="max-width: 640px;">
          <!-- Logo upload -->
          <div class="flex gap-3 items-center mb-3">
            <div>
              <strong style="font-size: 0.875rem; display: block; margin-bottom: 6px;">Логотип</strong>
              <img v-if="org?.logo_path" :src="'/uploads/' + org.logo_path.split('/uploads/').pop()" style="max-width: 120px; max-height: 60px; border: 1px solid var(--color-border); border-radius: 4px;" />
              <div v-else class="text-muted text-sm">Не загружен</div>
            </div>
            <div>
              <input type="file" accept="image/png,image/jpeg,image/svg+xml" @change="uploadLogo" style="display: none;" ref="logoInput" />
              <button class="btn btn-secondary btn-sm" @click="logoInput?.click()">Загрузить лого</button>
            </div>
          </div>

          <hr style="margin: 16px 0; border-color: var(--color-border);" />

          <!-- Signature upload -->
          <div class="flex gap-3 items-center mb-3">
            <div>
              <strong style="font-size: 0.875rem; display: block; margin-bottom: 6px;">Подпись</strong>
              <img v-if="org?.signature_path" :src="'/uploads/' + org.signature_path.split('/uploads/').pop()" style="max-width: 120px; max-height: 60px; border: 1px solid var(--color-border); border-radius: 4px;" />
              <div v-else class="text-muted text-sm">Не загружена</div>
            </div>
            <div>
              <input type="file" accept="image/png,image/jpeg" @change="uploadSignature" style="display: none;" ref="sigInput" />
              <button class="btn btn-secondary btn-sm" @click="sigInput?.click()">Загрузить подпись</button>
            </div>
          </div>

          <hr style="margin: 16px 0; border-color: var(--color-border);" />

          <!-- Footer banner upload -->
          <div class="flex gap-3 items-center">
            <div>
              <strong style="font-size: 0.875rem; display: block; margin-bottom: 6px;">Нижний баннер (футер)</strong>
              <img v-if="org?.footer_banner_path" :src="'/uploads/' + org.footer_banner_path.split('/uploads/').pop()" style="max-width: 200px; max-height: 40px; border: 1px solid var(--color-border); border-radius: 4px;" />
              <div v-else class="text-muted text-sm">Не загружен</div>
            </div>
            <div>
              <input type="file" accept="image/png,image/jpeg,image/svg+xml" @change="uploadFooterBanner" style="display: none;" ref="bannerInput" />
              <button class="btn btn-secondary btn-sm" @click="bannerInput?.click()">Загрузить баннер</button>
            </div>
          </div>
        </div>
      </div>

      <!-- USERS TAB -->
      <div v-if="activeTab === 'users'">
        <div class="card">
          <div class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th>ФИО</th>
                  <th>Email</th>
                  <th>Статус</th>
                  <th>Роль</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="u in users" :key="u.id">
                  <td>{{ u.full_name }}</td>
                  <td>{{ u.email }}</td>
                  <td>
                    <span :class="['badge', u.is_approved ? 'badge-sent' : 'badge-draft']">
                      {{ u.is_approved ? 'Одобрен' : 'Ожидает' }}
                    </span>
                  </td>
                  <td>{{ u.is_admin ? '👑 Admin' : 'User' }}</td>
                  <td>
                    <div class="flex gap-2">
                      <button v-if="!u.is_approved" class="btn btn-primary btn-sm" @click="approve(u.id)">Одобрить</button>
                      <button
                        v-if="u.id !== auth.user?.id"
                        class="btn btn-secondary btn-sm"
                        @click="toggleAdmin(u)"
                      >{{ u.is_admin ? 'Снять admin' : 'Сделать admin' }}</button>
                      <button v-if="u.id !== auth.user?.id" class="btn btn-danger btn-sm" @click="deleteUser(u.id)">Удалить</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- PROJECTS TAB -->
      <div v-if="activeTab === 'projects'">
        <div class="card">
          <div class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Название</th>
                  <th>Дата создания</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in allProjects" :key="p.id">
                  <td>{{ p.name }}</td>
                  <td>{{ formatDate(p.created_at) }}</td>
                  <td>
                    <button class="btn btn-danger btn-sm" @click="deleteProject(p.id)">Удалить</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </template>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import AppLayout from '../components/layout/AppLayout.vue'
import { useAuthStore } from '../stores/auth'
import { useOrgStore } from '../stores/org'
import { useProjectsStore } from '../stores/projects'
import api from '../api'

const auth = useAuthStore()
const orgStore = useOrgStore()
const projectsStore = useProjectsStore()

const activeTab = ref<'org' | 'users' | 'projects'>('org')
const orgTab = ref<'ooo' | 'ip' | 'files'>('ooo')
const orgSaved = ref(false)
const users = ref<any[]>([])
const logoInput = ref<HTMLInputElement | null>(null)
const sigInput = ref<HTMLInputElement | null>(null)
const bannerInput = ref<HTMLInputElement | null>(null)

const org = computed(() => orgStore.org)
const allProjects = computed(() => projectsStore.projects)

const orgForm = reactive({
  name: '', short_name: '', inn: '', ogrn: '', legal_address: '',
  bank_name: '', bik: '', account: '', corr_account: '', phone: '',
  signer_name: '', signer_role: '',
  ip_full_name: '', ip_inn: '', ip_ogrnip: '', ip_legal_address: '',
  ip_bank_name: '', ip_bik: '', ip_account: '', ip_corr_account: '',
  ip_phone: '', ip_signer_name: '', ip_signer_role: '',
})

onMounted(async () => {
  await Promise.all([orgStore.fetch(), projectsStore.fetchAll(), fetchUsers()])
  if (org.value) {
    Object.assign(orgForm, org.value)
  }
})

async function fetchUsers() {
  const res = await api.get('/users')
  users.value = res.data
}

async function saveOrg() {
  await orgStore.save(orgForm)
  orgSaved.value = true
  setTimeout(() => orgSaved.value = false, 2000)
}

async function uploadLogo(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  await orgStore.uploadLogo(file)
}

async function uploadSignature(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  await orgStore.uploadSignature(file)
}

async function uploadFooterBanner(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  await orgStore.uploadFooterBanner(file)
}

async function approve(id: number) {
  await api.patch(`/users/${id}/approve`)
  await fetchUsers()
}

async function toggleAdmin(u: any) {
  await api.patch(`/users/${u.id}/role`, { is_admin: !u.is_admin })
  await fetchUsers()
}

async function deleteUser(id: number) {
  if (!confirm('Удалить пользователя?')) return
  await api.delete(`/users/${id}`)
  await fetchUsers()
}

async function deleteProject(id: number) {
  if (!confirm('Удалить проект и все его письма?')) return
  await projectsStore.remove(id)
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('ru-RU')
}
</script>
