<!-- HomeView.vue 修改部分 -->
<script setup lang="ts">
import ChatBox from "../components/ChatBox.vue";
import { ref } from 'vue';

interface Conversation {
  id: string;
  title: string;
  messages: never[]; // 使用你在 ChatBox 中定义的 Message 接口
  timestamp: number;
}

// 示例数据
const conversations = ref<Conversation[]>([
  {
    id: '1',
    title: '对话 1',
    messages: [],
    timestamp: Date.now()
  },
  {
    id: '2',
    title: '对话 2',
    messages: [],
    timestamp: Date.now()
  }
]);

const activeConversationId = ref<string>('1');

// 新建对话
const createNewConversation = () => {
  const newConvo: Conversation = {
    id: Date.now().toString(),
    title: `对话 ${conversations.value.length + 1}`,
    messages: [],
    timestamp: Date.now()
  };
  conversations.value.push(newConvo);
  activeConversationId.value = newConvo.id;
};
</script>

<template>
  <div class="home-container">
    <el-container>
      <!-- 左侧导航 -->
      <el-aside width="240px" class="nav-aside">
        <div class="nav-header">
          <el-button type="primary" @click="createNewConversation">
            新建对话
          </el-button>
        </div>
        <el-menu :default-active="activeConversationId" @select="(id: string) => activeConversationId = id">
          <el-menu-item v-for="convo in conversations" :key="convo.id" :index="convo.id">
            <span>{{ convo.title }}</span>
            <div class="convo-subtitle">
              {{ convo.messages.length }} 条消息 ·
              {{ new Date(convo.timestamp).toLocaleDateString() }}
            </div>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 右侧聊天区域 -->
      <el-main class="chat-main">
        <ChatBox />
      </el-main>
    </el-container>
  </div>
</template>

<style scoped>
.home-container {
  height: 100vh;
  display: flex;
}

.nav-aside {
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
}

.nav-header {
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.el-menu {
  flex: 1;
  border-right: none;
}

.el-menu-item {
  height: auto !important;
  min-height: 64px;
  flex-direction: column;
  align-items: flex-start;
  padding: 12px 16px !important;
}

.convo-subtitle {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.chat-main {
  padding: 0;
  background-color: #f5f7fa;
}
</style>