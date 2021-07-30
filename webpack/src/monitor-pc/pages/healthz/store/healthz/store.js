import Vuex from 'vuex'
import Vue from 'vue'
Vue.use(Vuex)
const debug = process.env.NODE_ENV !== 'production'
export default new Vuex.Store({
  state: {
    globalData: [], // 获取到的全局数据
    displayedMetrics: [], // 要显示的后台服务器性能指标
    displayedMetricsDescription: {}, // 对应指标的中文描述，用于显示表头
    saasComponentNeedToTest: [], // saas组件中，需要进行测试的组件，由配置文件决定
    backendDataFlowComponent: [], // 监控后台数据流组件列表
    backendDependenciesComponent: [], // 监控后台依赖周边组件列表
    backendCollectorComponent: [], // 监控后台依赖周边组件列表
    saasDependenciesComponent: [], // 监控saas依赖周边组件列表
    PAGE_TOTAL: 4,
    selectedIPs: [], // 选中的ip地址列表
    allIPs: [], // 当前数据全部的ip地址列表
    serverIP: '' // 当前弹窗的ip
  },
  mutations: {
    loadBackendCollectorComponent(state, payload) {
      state.backendCollectorComponent = payload
    },
    loadGlobalData(state, payload) {
      // 加载全局数据
      state.globalData = payload
    },
    loadConfigSaasComponentNeedToTest(state, payload) {
      // 将数据从配置文件中加入到全局数据
      state.saasComponentNeedToTest = payload
    },
    loadConfigBackendDataFlowComponent(state, payload) {
      // 将数据从配置文件中加入到全局数据
      state.backendDataFlowComponent = payload
    },
    loadConfigBackendDependenciesComponent(state, payload) {
      // 将数据从配置文件中加入到全局数据
      state.backendDependenciesComponent = payload
    },
    loadConfigSaasDependenciesComponent(state, payload) {
      // 将数据从配置文件中加入到全局数据
      state.saasDependenciesComponent = payload
    },
    changeSelectedIPs(state, IPs) {
      state.selectedIPs = IPs
    },
    changeAllIPs(state, IPs) {
      state.allIPs = IPs
    },
    loadDisplayedMetrics(state, metrics) {
      state.displayedMetrics = metrics
    },
    loadDisplayedMetricsDescription(state, descriptions) {
      state.displayedMetricsDescription = descriptions
    },
    changeServerIP(state, ip) {
      state.serverIP = ip
    }
  },
  strict: debug
})
