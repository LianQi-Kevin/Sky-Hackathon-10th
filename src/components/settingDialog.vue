<script setup lang="ts">
import DB from "@/tools/db";
import type {FormInstance, FormRules} from "element-plus";

const settingDialogVisible = defineModel<boolean>('settingDialogVisible', {required: true})
const apiConfigs = defineModel<ApiConfigsType>('apiConfigs', {required: true})

const API_DB = new DB("ApiKeys", "nvApi");

export interface ApiConfigsType {
  NVIDIA_API_KEY?: string;
  client_id?: string;
}

const ruleFormRef = ref<FormInstance>()

const rules = reactive<FormRules<ApiConfigsType>>({
  NVIDIA_API_KEY: [{required: true, message: "API Key is required", trigger: "blur"}],
  client_id: [{required: false, message: "Client ID is required", trigger: "blur"}],
});

async function beforeClose(formEl: FormInstance | undefined) {
  if (!formEl) return // 非空
  // verify the API_KEY
  await formEl.validate(async (valid) => {
    if (valid && apiConfigs.value.NVIDIA_API_KEY?.startsWith("nvapi-")) {
      // 存数据库
      await API_DB.setItem("apiConfigs", toRaw(apiConfigs.value));
      settingDialogVisible.value = false;

    } else {
      ElMessage.error("Please check the input");
    }
  });
}
</script>

<template>
  <el-dialog
      v-model="settingDialogVisible"
      title="Setting"

      :before-close="() => {
        beforeClose(ruleFormRef)
      }"

      align-center
      destroy-on-close
      center
  >
    <el-form :model="apiConfigs" label-width="auto" label-position="left" status-icon :rules="rules" ref="ruleFormRef">
      <el-form-item label="Nvidia API Key">
        <el-input
            v-model="apiConfigs.NVIDIA_API_KEY"
            placeholder="Please Type NVIDIA_API_KEY Here"
            clearable
        />
      </el-form-item>
      <el-form-item label="Client ID">
        <el-input
            v-model="apiConfigs.client_id"
            placeholder="Please Type client_ID Here to load history"
            clearable
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="settingDialogVisible = false">Cancel</el-button>
      <el-button type="primary" @click="beforeClose(ruleFormRef)">Confirm</el-button>
    </template>
  </el-dialog>
</template>

<style scoped lang="scss">

</style>