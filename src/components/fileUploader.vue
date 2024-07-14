<script lang="ts" setup>
import {UploadFilled} from "@element-plus/icons-vue";
import type {
  UploadFile,
  UploadFiles,
  UploadInstance,
  UploadProps,
  UploadRawFile,

} from "element-plus";

import {fileAjaxUpload} from "@/network/fileUpload";


import { genFileId } from 'element-plus'
import type {ApiConfigsType} from "@/components/settingDialog.vue";

const apiConfigs = inject<ApiConfigsType>('apiConfigs')

interface propsType {
  process?: boolean;
  autoUpload?: boolean;
  accept_type?: string;
  upload_limit?: number;
}

const props = withDefaults(defineProps<propsType>(), {
  process: false,
  autoUpload: true,
  accept_type: 'image/jpeg,image/png',
  upload_limit: 1,
})

const uploadRef = ref<UploadInstance>()

const handleExceed: UploadProps['onExceed'] = (files) => {
  uploadRef.value!.clearFiles()
  const file = files[0] as UploadRawFile
  file.uid = genFileId()
  uploadRef.value!.handleStart(file)
}

const emit = defineEmits<{
  (e: 'onSuccess', response: any, uploadFile: UploadFile, uploadFiles: UploadFiles): void
  (e: 'onError', error: Error, uploadFile: UploadFile, uploadFiles: UploadFiles): void
}>()

</script>

<template>
  <el-upload
      ref="uploadRef"
      class="uploadMain"


      :accept="props.accept_type"
      :limit="props.upload_limit"
      :multiple="false"
      :show-file-list="true"
      action="#"

      :data="{process: props.process, client_id: apiConfigs?.client_id}"
      :http-request="fileAjaxUpload"

      :on-exceed="handleExceed"
      :on-success="(response, file, fileList) => emit('onSuccess', response, file, fileList)"
      :on-error="(error, file, fileList) => emit('onError', error, file, fileList)"
      :before-upload="(rawFile: UploadRawFile) => {
        // todo: check file size and type
        console.debug(rawFile);
        return true;
      }"

      :auto-upload="props.autoUpload"
      :drag="true"
  >
    <el-icon class="el-icon--upload"><upload-filled /></el-icon>
    <div class="el-upload__text">
      <el-text >拖拽 或 点击此处上传文件</el-text>
    </div>
    <template #tip>
      <div class="el-upload__tip">
        {{ "file size must be less than 50mb" }}
      </div>
    </template>
  </el-upload>
</template>

<style lang="scss" scoped>
:deep(.el-upload-dragger) {
  padding: 20px 10px;

  .el-icon--upload {
    font-size: 50px;
    margin-bottom: 5px;
  }
}
</style>