<script lang="ts" setup>
import {RouterView} from 'vue-router'
import mainHeader from '@/components/mainHeader.vue';
import type {ApiConfigsType} from "@/components/settingDialog.vue";
import {nanoid} from "nanoid";
import DB from "@/tools/db";

const apiConfigs = ref<ApiConfigsType>({})

provide('apiConfigs', apiConfigs)

onMounted(() => {
  nextTick(async () => {
    // 检查数据库内是否存在已保存数据，更新全局变量
    const API_DB = new DB("ApiKeys", "nvApi");
    const DB_res = await API_DB.getItem("apiConfigs");
    if (DB_res) {
        Object.assign(apiConfigs.value, DB_res);
      }

    // 如果client_id为空, 填充默认值
    if (!apiConfigs.value.client_id) {
      const date = new Date().getTime();
      const nano_id = nanoid(10);
      apiConfigs.value.client_id = `client_id_${date}_${nano_id}`;
    }

    // 填充默认值后存储
    await API_DB.setItem("apiConfigs", toRaw(apiConfigs.value));
  })
})
</script>

<template>
  <div class="mainContainer">
    <mainHeader />
    <RouterView style="flex-grow: 1"/>
  </div>
</template>

<style lang="scss" scoped>
.mainContainer {
  height: 100%;
  display: flex;
  flex-direction: column;
}
</style>
