<template>
  <AppLayout>
    <template #default>
      <div class="page-header">
        <h1 class="page-title">Настройки</h1>
      </div>

      <div class="tabs mb-6">
        <button :class="['tab-btn', activeTab === 'org' && 'active']" @click="activeTab = 'org'">Организация</button>
        <button :class="['tab-btn', activeTab === 'users' && 'active']" @click="activeTab = 'users'">
          Пользователи
          <span v-if="pendingCount" class="badge badge-pending" style="margin-left:6px; padding:1px 7px;">{{ pendingCount }}</span>
        </button>
        <button :class="['tab-btn', activeTab === 'projects' && 'active']" @click="activeTab = 'projects'">Проекты</button>
      </div>

      <!-- ── ORG TAB ──────────────────────────────────────────────────────── -->
      <div v-if="activeTab === 'org'">
        <div class="tabs tabs-sm mb-5">
          <button :class="['tab-btn', orgTab === 'ooo' && 'active']" @click="orgTab = 'ooo'">ООО</button>
          <button :class="['tab-btn', orgTab === 'ip' && 'active']" @click="orgTab = 'ip'">ИП</button>
          <button :class="['tab-btn', orgTab === 'files' && 'active']" @click="orgTab = 'files'">Файлы и шаблоны</button>
        </div>

        <!-- ООО form -->
        <div v-if="orgTab === 'ooo'" class="card" style="max-width: 680px;">
          <div class="card-title">Реквизиты ООО</div>
          <form @submit.prevent="saveOrg">
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:0 20px;">
              <div class="form-group" style="grid-column:1/-1;">
                <label>Полное название</label>
                <input v-model="orgForm.name" type="text" placeholder='Общество с ограниченной ответственностью "Название"' />
              </div>
              <div class="form-group">
                <label>Краткое название</label>
                <input v-model="orgForm.short_name" type="text" placeholder='ООО "Название"' />
              </div>
              <div class="form-group">
                <label>Телефон</label>
                <input v-model="orgForm.phone" type="text" placeholder="+7 (495) 000-00-00" />
              </div>
              <div class="form-group">
                <label>ИНН</label>
                <input v-model="orgForm.inn" type="text" placeholder="7700000000" />
              </div>
              <div class="form-group">
                <label>ОГРН</label>
                <input v-model="orgForm.ogrn" type="text" placeholder="1234567890123" />
              </div>
              <div class="form-group" style="grid-column:1/-1;">
                <label>Юридический адрес</label>
                <input v-model="orgForm.legal_address" type="text" placeholder="105082, г. Москва, ул. Примерная, д. 1" />
              </div>
              <div class="form-group" style="grid-column:1/-1;">
                <label>Банк</label>
                <input v-model="orgForm.bank_name" type="text" placeholder="ПАО Сбербанк" />
              </div>
              <div class="form-group">
                <label>БИК</label>
                <input v-model="orgForm.bik" type="text" placeholder="044525225" />
              </div>
              <div class="form-group">
                <label>Расчётный счёт</label>
                <input v-model="orgForm.account" type="text" placeholder="40702810000000000000" />
              </div>
              <div class="form-group">
                <label>Корр. счёт</label>
                <input v-model="orgForm.corr_account" type="text" placeholder="30101810400000000225" />
              </div>
              <div class="form-group">
                <label>ФИО подписанта</label>
                <input v-model="orgForm.signer_name" type="text" placeholder="Иванов И.И." />
              </div>
              <div class="form-group">
                <label>Должность подписанта</label>
                <input v-model="orgForm.signer_role" type="text" placeholder="Директор" />
              </div>
            </div>

            <div v-if="orgSaved" class="alert alert-success mb-4">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0"><polyline points="20 6 9 17 4 12"/></svg>
              Реквизиты сохранены
            </div>
            <button type="submit" class="btn btn-primary">Сохранить реквизиты</button>
          </form>
        </div>

        <!-- ИП form -->
        <div v-if="orgTab === 'ip'" class="card" style="max-width: 680px;">
          <div class="card-title">Реквизиты ИП</div>
          <form @submit.prevent="saveOrg">
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:0 20px;">
              <div class="form-group" style="grid-column:1/-1;">
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
              <div class="form-group" style="grid-column:1/-1;">
                <label>Юридический адрес</label>
                <input v-model="orgForm.ip_legal_address" type="text" />
              </div>
              <div class="form-group" style="grid-column:1/-1;">
                <label>Банк</label>
                <input v-model="orgForm.ip_bank_name" type="text" />
              </div>
              <div class="form-group">
                <label>БИК</label>
                <input v-model="orgForm.ip_bik" type="text" />
              </div>
              <div class="form-group">
                <label>Расчётный счёт</label>
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
            <div v-if="orgSaved" class="alert alert-success mb-4">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0"><polyline points="20 6 9 17 4 12"/></svg>
              Реквизиты сохранены
            </div>
            <button type="submit" class="btn btn-primary">Сохранить реквизиты</button>
          </form>
        </div>

        <!-- Files & templates -->
        <div v-if="orgTab === 'files'" class="card" style="max-width: 680px;">
          <div class="card-title">Файлы организации</div>

          <div class="upload-item">
            <div class="upload-preview">
              <img v-if="org?.logo_path" :src="'/uploads/' + org.logo_path.split('/uploads/').pop()" />
              <div v-else style="width:80px;height:48px;background:var(--bg);border:1px dashed var(--border);border-radius:var(--r);display:flex;align-items:center;justify-content:center;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--subtle)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
              </div>
            </div>
            <div class="upload-info">
              <div class="upload-label">Логотип</div>
              <div class="upload-desc">PNG, JPG или SVG — отображается в шапке письма</div>
            </div>
            <div>
              <input type="file" accept="image/png,image/jpeg,image/svg+xml" @change="uploadLogo" style="display:none;" ref="logoInput" />
              <button class="btn btn-secondary btn-sm" @click="logoInput?.click()">Загрузить</button>
            </div>
          </div>

          <div class="upload-item">
            <div class="upload-preview">
              <img v-if="org?.signature_path" :src="'/uploads/' + org.signature_path.split('/uploads/').pop()" />
              <div v-else style="width:80px;height:48px;background:var(--bg);border:1px dashed var(--border);border-radius:var(--r);display:flex;align-items:center;justify-content:center;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--subtle)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 20H7L3 7l4 1 5-4 5 4 4-1-1 13z"/></svg>
              </div>
            </div>
            <div class="upload-info">
              <div class="upload-label">Подпись</div>
              <div class="upload-desc">PNG или JPG — ставится рядом с именем подписанта</div>
            </div>
            <div>
              <input type="file" accept="image/png,image/jpeg" @change="uploadSignature" style="display:none;" ref="sigInput" />
              <button class="btn btn-secondary btn-sm" @click="sigInput?.click()">Загрузить</button>
            </div>
          </div>

          <div class="upload-item">
            <div class="upload-preview">
              <img v-if="org?.footer_banner_path" :src="'/uploads/' + org.footer_banner_path.split('/uploads/').pop()" />
              <div v-else style="width:80px;height:48px;background:var(--bg);border:1px dashed var(--border);border-radius:var(--r);display:flex;align-items:center;justify-content:center;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--subtle)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="17" x2="21" y2="17"/></svg>
              </div>
            </div>
            <div class="upload-info">
              <div class="upload-label">Нижний баннер</div>
              <div class="upload-desc">Отображается в футере каждого письма</div>
            </div>
            <div>
              <input type="file" accept="image/png,image/jpeg,image/svg+xml" @change="uploadFooterBanner" style="display:none;" ref="bannerInput" />
              <button class="btn btn-secondary btn-sm" @click="bannerInput?.click()">Загрузить</button>
            </div>
          </div>

          <div class="divider"></div>
          <div class="card-title" style="font-size:13.5px; color:var(--muted); font-weight:600; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:12px;">Шаблоны DOCX</div>

          <div class="upload-item">
            <div class="upload-info">
              <div class="upload-label">Шаблон ООО</div>
              <div class="upload-desc">
                .docx с плейсхолдерами:
                <span v-for="ph in placeholders" :key="ph"><code>{{ placeholderLabel(ph) }}</code> </span>
              </div>
              <div v-if="org?.template_ooo_path" class="mt-1" style="font-size:12.5px; color:var(--success); display:flex; align-items:center; gap:4px;">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                Шаблон загружен
              </div>
              <div v-else class="upload-desc mt-1">Не загружен — используется стандартная генерация</div>
            </div>
            <div>
              <input type="file" accept=".docx" @change="uploadTemplateOoo" style="display:none;" ref="templateOooInput" />
              <button class="btn btn-secondary btn-sm" @click="templateOooInput?.click()">Загрузить</button>
            </div>
          </div>

          <div class="upload-item">
            <div class="upload-info">
              <div class="upload-label">Шаблон ИП</div>
              <div class="upload-desc">Те же плейсхолдеры, что и для ООО</div>
              <div v-if="org?.template_ip_path" class="mt-1" style="font-size:12.5px; color:var(--success); display:flex; align-items:center; gap:4px;">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                Шаблон загружен
              </div>
              <div v-else class="upload-desc mt-1">Не загружен — используется стандартная генерация</div>
            </div>
            <div>
              <input type="file" accept=".docx" @change="uploadTemplateIp" style="display:none;" ref="templateIpInput" />
              <button class="btn btn-secondary btn-sm" @click="templateIpInput?.click()">Загрузить</button>
            </div>
          </div>
        </div>
      </div>

      <!-- ── USERS TAB ────────────────────────────────────────────────────── -->
      <div v-if="activeTab === 'users'">
        <div class="card">
          <div v-if="!users.length" class="empty-state" style="padding:24px;">
            <div class="empty-state-title">Нет пользователей</div>
          </div>
          <div v-else class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Пользователь</th>
                  <th>Email</th>
                  <th style="width:110px;">Статус</th>
                  <th style="width:110px;">Роль</th>
                  <th style="width:200px;"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="u in users" :key="u.id">
                  <td>
                    <div class="flex items-center gap-2">
                      <div style="width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,#6366F1,#8B5CF6);display:flex;align-items:center;justify-content:center;color:#fff;font-size:11px;font-weight:700;flex-shrink:0;">
                        {{ u.full_name.split(' ').slice(0,2).map((w: string) => w[0]).join('').toUpperCase() }}
                      </div>
                      <span class="font-medium" style="color:var(--text);">{{ u.full_name }}</span>
                    </div>
                  </td>
                  <td class="text-muted">{{ u.email }}</td>
                  <td>
                    <span :class="['badge', u.is_approved ? 'badge-approved' : 'badge-pending']">
                      {{ u.is_approved ? 'Одобрен' : 'Ожидает' }}
                    </span>
                  </td>
                  <td>
                    <span v-if="u.is_admin" class="badge badge-admin">Админ</span>
                    <span v-else class="text-muted text-sm">Польз.</span>
                  </td>
                  <td>
                    <div class="flex gap-2 justify-end">
                      <button v-if="!u.is_approved" class="btn btn-primary btn-sm" @click="approve(u.id)">Одобрить</button>
                      <button
                        v-if="u.id !== auth.user?.id"
                        class="btn btn-secondary btn-sm"
                        @click="toggleAdmin(u)"
                      >{{ u.is_admin ? 'Снять права' : 'Сделать адм.' }}</button>
                      <button v-if="u.id !== auth.user?.id" class="btn btn-danger btn-sm" @click="deleteUser(u.id)">Удалить</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- ── PROJECTS TAB ─────────────────────────────────────────────────── -->
      <div v-if="activeTab === 'projects'">
        <div class="card">
          <div v-if="!allProjects.length" class="empty-state" style="padding:24px;">
            <div class="empty-state-title">Нет проектов</div>
          </div>
          <div v-else class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Название проекта</th>
                  <th style="width:140px;">Дата создания</th>
                  <th style="width:80px;"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in allProjects" :key="p.id">
                  <td class="font-medium" style="color:var(--text);">{{ p.name }}</td>
                  <td class="text-muted">{{ formatDate(p.created_at) }}</td>
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
const templateOooInput = ref<HTMLInputElement | null>(null)
const templateIpInput = ref<HTMLInputElement | null>(null)

const org = computed(() => orgStore.org)
const allProjects = computed(() => projectsStore.projects)
const pendingCount = computed(() => users.value.filter(u => !u.is_approved).length)

const placeholders = ['number','date','recipient','subject','body','signer_role','signer_name','executor_name','executor_phone']

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
  if (org.value) Object.assign(orgForm, org.value)
})

async function fetchUsers() {
  const res = await api.get('/users')
  users.value = res.data
}

async function saveOrg() {
  await orgStore.save(orgForm)
  orgSaved.value = true
  setTimeout(() => orgSaved.value = false, 2500)
}

async function uploadLogo(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) await orgStore.uploadLogo(file)
}
async function uploadSignature(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) await orgStore.uploadSignature(file)
}
async function uploadFooterBanner(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) await orgStore.uploadFooterBanner(file)
}
async function uploadTemplateOoo(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) await orgStore.uploadTemplateOoo(file)
}
async function uploadTemplateIp(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) await orgStore.uploadTemplateIp(file)
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

function placeholderLabel(ph: string) { return '{{' + ph + '}}' }

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' })
}
</script>
