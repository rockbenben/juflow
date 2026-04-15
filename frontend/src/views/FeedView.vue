<script setup lang="ts">
import { onMounted, ref } from 'vue'
import Sidebar from '../components/Sidebar.vue'
import ArticleList from '../components/ArticleList.vue'
import ReadingPane from '../components/ReadingPane.vue'
import AddSubscription from '../components/AddSubscription.vue'
import EditSubscription from '../components/EditSubscription.vue'
import OnboardingModal from '../components/OnboardingModal.vue'
import MobileNav from '../components/MobileNav.vue'
import KeyboardHelp from '../components/KeyboardHelp.vue'
import { useArticlesStore } from '../stores/articles'
import { useSubscriptionsStore } from '../stores/subscriptions'
import { useWebSocket } from '../composables/useWebSocket'
import { useKeyboard } from '../composables/useKeyboard'

const articles = useArticlesStore()
const subs = useSubscriptionsStore()
const showAddModal = ref(false)
const showOnboarding = ref(false)
const editSubscriptionId = ref<string | null>(null)
const mobileTab = ref('feed')

useWebSocket()
const { showHelp } = useKeyboard()

onMounted(async () => {
  await Promise.all([articles.load(), subs.load()])
  // Show onboarding for new users with no subscriptions
  if (subs.subscriptions.length === 0 && !localStorage.getItem('onboarding_done')) {
    showOnboarding.value = true
  }
})

function closeOnboarding() {
  showOnboarding.value = false
  localStorage.setItem('onboarding_done', '1')
  // Reload subscriptions and articles after onboarding
  subs.load()
  articles.load()
}

async function onMobileTab(tab: string) {
  mobileTab.value = tab
  if (tab === 'feed') {
    await articles.load()
  } else if (tab === 'favorites') {
    await articles.loadFavorites()
  }
}
</script>

<template>
  <div class="feed-layout">
    <Sidebar
      @add-subscription="showAddModal = true"
      @edit-subscription="editSubscriptionId = $event"
    />
    <ArticleList />
    <ReadingPane />
  </div>
  <MobileNav :tab="mobileTab" @tab="onMobileTab" />
  <AddSubscription v-if="showAddModal" @close="showAddModal = false" />
  <EditSubscription
    v-if="editSubscriptionId"
    :subscription-id="editSubscriptionId"
    @close="editSubscriptionId = null"
  />
  <KeyboardHelp v-if="showHelp" @close="showHelp = false" />
  <OnboardingModal v-if="showOnboarding" @close="closeOnboarding" />
</template>

<style scoped>
.feed-layout { display: flex; height: 100vh; background: var(--bg-primary); }

@media (max-width: 768px) {
  .feed-layout { flex-direction: column; }
  .feed-layout > :deep(.sidebar) { display: none; }
  .feed-layout > :deep(.article-list) { width: 100%; }
  .feed-layout > :deep(.reading-pane) { position: fixed; inset: 0; z-index: 40; }
}
</style>
