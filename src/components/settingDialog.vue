<script setup lang="ts">
import DB from "@/tools/db";
import { nanoid } from 'nanoid'
import type {FormInstance, FormRules} from "element-plus";

const settingDialogVisible = defineModel<boolean>('settingDialogVisible', {required: true})

const emit = defineEmits<{
  onSubmit: [apiConfigs: ApiConfigsType]
}>()

const API_DB = new DB("ApiKeys", "nvApi");

interface ApiConfigsType {
  NVIDIA_API_KEY?: string;
  client_id?: string;
}

const apiConfigs = reactive<ApiConfigsType>({});

const ruleFormRef = ref<FormInstance>()

const rules = reactive<FormRules<ApiConfigsType>>({
  NVIDIA_API_KEY: [{required: true, message: "API Key is required", trigger: "blur"}],
  client_id: [{required: false, message: "Client ID is required", trigger: "blur"}],
});

async function beforeClose(formEl: FormInstance | undefined) {
  if (!formEl) return // 非空
  // verify the API_KEY
  await formEl.validate(async (valid) => {
    if (valid && apiConfigs.NVIDIA_API_KEY?.startsWith("nvapi-")) {
      // 存数据库
      await API_DB.setItem("apiConfigs", toRaw(apiConfigs));
      settingDialogVisible.value = false;

      // 保存时回调
      emit("onSubmit", toRaw(apiConfigs));
    } else {
      ElMessage.error("Please check the input");
    }
  });
}

onMounted(() => {
  nextTick(() => {
    // 检查数据库内是否存在已保存数据，更新全局变量
    API_DB.getItem("apiConfigs").then((res) => {
      if (res) {
        Object.assign(apiConfigs, res);
      }
    });

    // 如果client_id为空, 填充默认值
    if (!apiConfigs.client_id) {
      const date = new Date().toLocaleDateString();
      const nano_id = nanoid(10);
      apiConfigs.client_id = `client_id_${date}_${nano_id}`;
    }
  });
});
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