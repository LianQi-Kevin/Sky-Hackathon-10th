<script setup lang="ts">
import md from '@/markdown/markdown'
import {CopyDocument, Help} from "@element-plus/icons-vue";
import CodeCard from "@/components/codeCard.vue";
import {useClipboard, useThrottleFn} from "@vueuse/core";

import "@/styles/github-markdown.css"
import {ElMessage} from "element-plus";

interface propsType {
  role: 'user' | 'system' | 'assistant';
  content: string;
  files?: File[];
}

const props = defineProps<propsType>()

const throttledReplaceCodeCard = useThrottleFn(replaceCodeCard, 500);
const codeBlocksContainer = ref<any>();

onMounted(() => {
  nextTick(() => {
    throttledReplaceCodeCard()
  });
})

function replaceCodeCard() {
  // 获取 codeBlocksContainer 的实际 DOM 元素
  const containerElement = codeBlocksContainer.value;

  if (containerElement) {
    const codeBlocks = containerElement.querySelectorAll('pre[id="codeSpace"]');

    codeBlocks.forEach((block: Element) => {
      const code = block.querySelector('code[class*="language-"]');
      if (code) {
        const content = code.textContent;
        // 使用默认值 'plaintext' 如果没有找到语言类
        const lang = code.className.replace('language-', '') || 'plaintext';

        // 创建 CodeCard 实例并替换当前的 pre 元素
        // 传递 lang, content, 以及 theme (如果需要的话)
        const codeCardInstance = createApp(CodeCard, { lang, content });
        const mountNode = document.createElement('div');
        block.replaceWith(mountNode);
        codeCardInstance.mount(mountNode);
      }
    });
  }
}

const { copy, copied, isSupported } = useClipboard()
const throttledCopy = useThrottleFn(copyContent, 500);
function copyContent() {
  if (isSupported) {
    if (props.content.length === 0) {
      ElMessage({
        message: 'Fail to copy, content is Empty',
        type: 'warning'
      })
    } else {
      copy(props.content)
      if(copied){
        console.debug(`Copied to clipboard: ${props.content}`)
      }
    }
  } else {
    ElMessage({
      message: 'Your browser does not support copying',
      type: 'error'
    })
  }
}
</script>

<template>
  <div class="flexBox">
    <div v-if="props.role === 'user'" class="userMessage">
      {{ props.content }}
    </div>

    <div v-else-if="props.role === 'assistant'" class="assistantMessage">
      <el-icon class="icon"><Help /></el-icon>
      <div class="messageMainBox">
        <article ref="codeBlocksContainer" class="markdown-body">
          <div class="markdown" v-html="md.render(props.content)"/>
        </article>

        <div class="assistantToolBar">
          <el-button link @click="throttledCopy">
            <el-icon><CopyDocument /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

  </div>
</template>

<style lang="scss" scoped>
.flexBox {
  display: flex;
  flex-direction: column;

  padding: 18px 20px;

  .userMessage {
    max-width: 70%;
    margin: 0 0 0 auto;

    padding: 10px 20px;

    // border
    border: 1px solid var(--el-border-color-light);
    border-radius: 1.5rem;

    // text
    word-wrap: break-word;
    white-space: pre-wrap;
    //line-height: 1.5rem;
  }

  .assistantMessage {
    display: flex;
    flex-direction: row;
    gap: 1.5rem;

    flex-grow: 1;

    .icon {
      // center display
      display: flex;
      align-items: center;
      overflow: hidden;

      // border
      border: 1px solid var(--el-border-color-light);
      border-radius: 9999px;
      min-width: 32px;
      min-height: 32px;
    }

    .messageMainBox {
      display: flex;
      flex-direction: column;
      gap: 1rem;

      .markdown-body {
        width: 100%;
      }

      .assistantToolBar {
        svg {
          display: none;
        }
      }
    }

    .messageMainBox:active, .messageMainBox:hover {
      .assistantToolBar {
        svg {
          display: block;
        }
      }
    }
  }
}

.flexBox:last-child .assistantMessage .messageMainBox .assistantToolBar svg {
  display: block;
}
</style>