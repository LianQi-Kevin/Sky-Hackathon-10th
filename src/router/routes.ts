import ChatView from "@/views/ChatView.vue";
import type {RouteRecordRaw} from "vue-router";

const routes: RouteRecordRaw[] = [
  {
    path: "/",
    alias: "/home",
    name: "Chat",
    component: ChatView,
    meta: {
      title: "Chat"
    }
  },
  {
    path: "/draw",
    name: "Draw",
    component: () => import("@/views/DrawView.vue"),
    meta: {
      title: "Draw"
    }
  },
  {
    path: "/about",
    name: "About",
    component: () => import("@/views/AboutView.vue"),
    meta: {
      title: "About"
    }
  },
  {
    path: '/error/:id',
    component: () => import('@/views/notFound.vue'),
    props: true,
    meta: {
      title: 'ERROR',
    }
  },
  {
    // 配置全局匹配，跳转到 404 NOT FOUND
    path: '/:pathMatch(.*)*',
    redirect: '/error/404'
  }
]

export default routes