<script setup lang="ts">
import { toastMessage } from './composables/useWebSocket'
</script>

<template>
  <router-view />
  <Transition name="toast">
    <div v-if="toastMessage" class="toast">{{ toastMessage }}</div>
  </Transition>
</template>

<style>
.toast {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--error);
  color: #fff;
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 13px;
  z-index: 9999;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
.toast-enter-active, .toast-leave-active { transition: opacity 0.3s, transform 0.3s; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateX(-50%) translateY(10px); }
</style>
