<script lang="ts" setup>
import chatInputArea from "@/components/chatInputArea.vue";
import FileUploader from "@/components/fileUploader.vue";

// File Upload Actions
const modeSwitchRef = ref<boolean>(false)

// Chat Messages Tools
interface ChatMessage {
  role: 'user' | 'system' | 'assistant';
  content: string;
}

const chatMessagesLists = ref<ChatMessage[]>([])

// Prompt Input Actions
const inputValue = ref<string>('')
const submitLoading = ref<boolean>(false)

function submitMessage() {
  console.log(inputValue.value)
  chatMessagesLists.value.push({role: 'user', content: inputValue.value})
  // clear input value
  inputValue.value = ''

  // move scrollbar to bottom
  nextTick(() => {
    const chatMessages = document.querySelector('.chatMessages')
    if (chatMessages) {
      chatMessages.scrollTop = chatMessages.scrollHeight
    }
  })
}
</script>

<template>
  <div class="container">
    <div class="chatContainer">
      <div class="chatMessages" v-show="chatMessagesLists.length === 0">
        <el-empty style="height: 100%;">
          <template #default >
            <h2>欢迎使用国标咨询工具</h2>
            <p v-if="modeSwitchRef">请在上传您的设计参数文档以进行校验</p>
            <p v-else>请在下方输入框输入您的问题</p>
          </template>
        </el-empty>
      </div>
      <div class="chatMessages" v-show="chatMessagesLists.length !== 0">
        <template v-for="(message, index) in chatMessagesLists" :key="index">
          <chat-message :content="message.content" :role="message.role"/>
        </template>
      </div>

      <chatInputArea v-model:inputValue="inputValue" v-model:submitLoading="submitLoading" @submit="submitMessage" v-if="!modeSwitchRef"/>
    </div>

    <div class="fileUploadArea">
      <div class="fileUploadArea__ModeSwitch">
        <el-switch v-model="modeSwitchRef" active-text="方案对比" inactive-text="对话咨询" size="large"/>
      </div>

      <div class="uploadArea">
        <div class="standard">
          <h4>国家标准</h4>
          <el-select>

          </el-select>
          <file-uploader accept_type="application/pdf" @fileUpload="(option) => {console.log(option)}"/>
        </div>
        <el-divider v-if="modeSwitchRef" />
        <div class="userFile" v-if="modeSwitchRef">
          <h4>用户文件</h4>
          <file-uploader accept_type="application/pdf" @fileUpload="(option) => {console.log(option)}"/>
        </div>
      </div>
    </div>

  </div>
</template>

<style lang="scss" scoped>
.container {
  height: 100%;
  width: 100%;
  max-width: 1000px;
  margin: 0 auto;
  padding: 10px 0 10px 0;


  display: flex;
  flex-direction: row;
  justify-content: start;
  gap: 15px;

  overflow: hidden;

  .chatContainer {
    height: 100%;
    width: 100%;

    display: flex;
    flex-direction: column;
    gap: 10px;

    ::-webkit-scrollbar {
      display: block;
    }

    .chatMessages{
      flex-grow: 1;
      overflow-y: auto;
      overflow-x: hidden;

      :deep(.el-empty__description) {
        display: none;
      }

      .chatMessage {
        font-size: 1rem;
      }
    }
  }

  .fileUploadArea {
    width: 100%;
    max-width: 250px;

    display: flex;
    flex-direction: column;
    gap: 10px;

    .fileUploadArea__ModeSwitch {
      display: flex;
      justify-content: center;

      border-radius: 6px;
      border: 1px dashed var(--el-border-color)
    }
  }

  @media only screen and (max-width: 600px) {
    .fileUploadArea {
      display: none;
    }
  }
}
</style>