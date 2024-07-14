<script lang="ts" setup>
import chatInputArea from "@/components/chatInputArea.vue";
import FileUploader from "@/components/fileUploader.vue";
import {ElMessage} from "element-plus";
import type {ApiConfigsType} from "@/components/settingDialog.vue";
import {WSS_embedding} from "@/network/websockers";


// File Upload Actions
const modeSwitchRef = ref<boolean>(false)
const standardModeRef = ref<boolean>(false)

const apiConfigs = inject<ApiConfigsType>('apiConfigs')

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


// 国标及设计参数文件 todo: 临时能用
interface fileInfo {
  file_uuid: string;
  filename: string;
}

interface fileUploadSuccessResponse extends fileInfo{
  message: string
  client_id: string
}

const standard_file = ref<fileInfo>({
  file_uuid: '',
  filename: ''
})
const parameter_file = ref<fileInfo>({
  file_uuid: '',
  filename: ''
})
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

      <el-button v-if="modeSwitchRef" round style="padding: 10px;margin: 0 10px 10px 20px;">开始对比</el-button>
      <chatInputArea v-model:inputValue="inputValue" v-model:submitLoading="submitLoading" @submit="submitMessage" v-else/>
    </div>

    <div class="fileUploadArea">
      <div class="fileUploadArea__ModeSwitch">
        <el-switch v-model="modeSwitchRef" active-text="方案对比" inactive-text="对话咨询" size="large"/>
      </div>

      <div class="uploadArea">
        <div class="standard">
          <div class="standard__title" style="display: flex; flex-direction: row; justify-content: space-between; align-items: baseline">
            <h4>国家标准</h4>
            <el-switch v-model="standardModeRef" active-text="选择现有标准" inactive-text="上传新标准" size="small" disabled/>
          </div>
          <el-select
            v-show="standardModeRef"
          >

          </el-select>

          <file-uploader
            v-show="!standardModeRef"

            :accept_type="'application/pdf'"
            :auto-upload="true"
            :process="true"
            @on-success="(response: fileUploadSuccessResponse) => {
              console.log(response)
              if (response.message) {
                ElMessage({
                  message: response.message,
                  type: 'success'
                })
              }

              // update standard file
              standard_file = {
                file_uuid: response.file_uuid,
                filename: response.filename
              }

              // start embedding
              WSS_embedding(
                apiConfigs?.NVIDIA_API_KEY as string,
                apiConfigs?.client_id as string,
                response.file_uuid as string,
                (status) => {
                  console.log(status)
                }
              )
            }"
            @on-error="(error) => {ElMessage({
              message: error.name + ': ' + error.message,
              type: 'error'
            })}"
          />
        </div>
        <el-divider v-if="modeSwitchRef" />
        <div class="userFile" v-if="modeSwitchRef">
          <h4>用户文件</h4>
          <file-uploader
            :accept_type="'application/pdf,.md,text/plain,application/vnd.openxmlformats-officedocument.wordprocessingml.document'"
            :process="false"
            @on-success="(response:  fileUploadSuccessResponse) => {
              console.log(response)
              if (response.message) {
                ElMessage({
                  message: response.message,
                  type: 'success'
                })
              }

              // update parameter file
              parameter_file = {
                file_uuid: response.file_uuid,
                filename: response.filename
              }
            }"
            @on-error="(error) => {ElMessage({
              message: error.name + ': ' + error.message,
              type: 'error'
            })}"
          />
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
    max-width: 260px;

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