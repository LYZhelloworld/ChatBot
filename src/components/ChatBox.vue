<template>
  <div class="chat-container">
    <el-container class="container-wrapper">
      <!-- 聊天记录区域 -->
      <el-main class="chat-history">
        <div 
          v-for="(msg, index) in messages"
          :key="index"
          class="message"
          :class="{ 'user-message': msg.isUser }"
        >
          <div class="message-content">
            {{ msg.content }}
          </div>
          <div class="message-time">
            {{ formatTime(msg.timestamp) }}
          </div>
        </div>
      </el-main>

      <!-- 输入框区域 -->
      <el-footer class="input-footer">
        <div class="input-container">
          <el-input
            v-model="inputMessage"
            placeholder="输入消息..."
            @keyup.enter="sendMessage"
            resize="none"
            type="textarea"
            autosize
          />
          <el-button
            type="primary"
            @click="sendMessage"
            class="send-button"
          >
            发送
          </el-button>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue'

const messages = ref<{content: string, timestamp: number, isUser: boolean}[]>([])
const inputMessage = ref('')

// 初始化示例消息
onMounted(() => {
  messages.value = [
    {
      content: '欢迎使用聊天系统！',
      timestamp: new Date().getTime() - 3600000,
      isUser: false
    }
  ]
  scrollToBottom()
})

// 发送消息
const sendMessage = () => {
  if (!inputMessage.value.trim()) return

  // 添加用户消息
  messages.value.push({
    content: inputMessage.value.trim(),
    timestamp: new Date().getTime(),
    isUser: true
  })

  // 清空输入框
  inputMessage.value = ''

  // 模拟回复（实际应替换为 API 调用）
  setTimeout(() => {
    messages.value.push({
      content: '已收到您的消息：' + messages.value[messages.value.length - 1].content,
      timestamp: new Date().getTime(),
      isUser: false
    })
    scrollToBottom()
  }, 1000)

  // 滚动到底部
  nextTick(() => {
    scrollToBottom()
  })
}

// 滚动到底部
const scrollToBottom = () => {
  const container = document.querySelector('.chat-history')
  if (container) {
    container.scrollTop = container.scrollHeight
  }
}

// 格式化时间
const formatTime = (timestamp: number) => {
  return new Date(timestamp).toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}
</script>

<style scoped>
.chat-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.container-wrapper {
  height: 100%;
}

.chat-history {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.message {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 12px;
  margin: 5px 0;
  animation: fadeIn 0.3s ease-in;
}

.user-message {
  background-color: #409eff;
  color: white;
  margin-left: auto;
}

.message:not(.user-message) {
  background-color: #f5f7fa;
  margin-right: auto;
}

.message-content {
  word-break: break-word;
}

.message-time {
  font-size: 0.75rem;
  color: rgba(0, 0, 0, 0.5);
  margin-top: 4px;
  text-align: right;
}

.user-message .message-time {
  color: rgba(255, 255, 255, 0.8);
}

.input-footer {
  padding: 20px;
  background-color: #fff;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
}

.input-container {
  display: flex;
  gap: 10px;
}

.send-button {
  align-self: flex-end;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>