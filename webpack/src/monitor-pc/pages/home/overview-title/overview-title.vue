<template>
  <section class="title">
    <span class="header"> {{ $t('监控资源概览') }} </span>
    <div class="content">
      <svg-icon icon-name="arrow-right" class-name="right-arrow" :class="{ 'canClick': canLeft }"
                @click="pullClickHandle('left')"></svg-icon>
      <svg-icon icon-name="arrow-left" :class="{ 'canClick': canRight }" class="left-arrow"
                @click="pullClickHandle('right')"></svg-icon>
      <div class="overview-list-wrap" ref="overviewListWrap">
        <ul class="overview-list clearfix" :style="{ marginLeft: curLeft + 'px' }">
          <li class="item" v-for="(item,index) in overview" :class="{ 'item-last': item.last }"
              :key="index">
            <span @click="goToBpPage(item.pageType,item)">
              <bk-popover :content="getIconContent(item)" placement="top">
                <svg-icon class-name="item__icon" :icon-name="getIconClass(item)"></svg-icon>
              </bk-popover>
            </span>
            <span class="item__abnormal"
                  @click="item.abnormal && goToBpDetailPage(item)">{{item.abnormal}}</span>
            /
            <span class="item__normal">{{item.normal}}</span>
          </li>
        </ul>
      </div>
    </div>
  </section>
</template>

<script>
import SvgIcon from '../../../components/svg-icon/svg-icon'
import { gotoPageMixin } from '../../../common/mixins'

export default {
  name: 'overview-title',
  components: {
    SvgIcon
  },
  mixins: [gotoPageMixin],
  props: {
    overview: {
      type: Array,
      default() {
        return []
      }
    }
  },
  data() {
    return {
      itemWidth: 134.5,
      curIndex: 0,
      lastIndex: 0,
      curLeft: 0,
      isClick: false,
      componentIconMap: {
        [this.$t('数据库')]: 'database',
        [this.$t('http服务')]: 'http',
        [this.$t('消息队列')]: 'message-queue',
        [this.$t('服务拨测')]: 'uptimecheck'
      },
      iconContentMap: {
        linux: 'Linux',
        windows: 'Windows',
        aix: 'AIX'
      }
    }
  },
  computed: {
    pullWidth() {
      return -this.itemWidth * this.curIndex
    },
    canLeft() {
      return this.lastIndex && this.curIndex < this.lastIndex
    },
    canRight() {
      return this.lastIndex && this.curIndex > 0
    }
  },
  mounted() {
    this.lastIndex = this.overview.length - Math.floor(this.$refs.overviewListWrap.clientWidth / this.itemWidth)
  },
  methods: {
    pullClickHandle(key) {
      if (key === 'left' && this.curIndex < this.lastIndex && !this.isClick) {
        this.curIndex += 1
        this.animate()
      } else if (key === 'right' && this.curIndex > 0 && !this.isClick) {
        this.curIndex -= 1
        this.animate()
      }
    },
    animate() {
      const createTime = function () {
        return (+new Date())
      }
      const duration = 700
      const startTime = createTime()
      this.isClick = true
      const inter = setInterval(() => {
        const remaining = Math.max(0, startTime + duration - createTime())
        const temp = remaining / duration || 0
        const percent = 1 - temp
        const leftPos = ((this.pullWidth - this.curLeft) * percent) + this.curLeft
        this.curLeft = leftPos
        if (this.pullWidth === leftPos) {
          clearInterval(inter)
          this.isClick = false
        }
      }, 20)
    },
    goToBpPage(type, item) {
      if (type === 'host' && item.extra.all_ip_list.length) {
        localStorage.setItem('home-host-all-ip-list', item.extra.all_ip_list.join('\n'))
        this.commonGotoPage('bp/?fromhome=1')
      } else if (type === 'component' && item.extra) {
        this.commonGotoPage(`component/?model=${item.extra.id}`)
      } else if (type === 'uptimecheck') {
        this.commonGotoPage('uptime_check/')
      }
    },
    goToBpDetailPage(item) {
      if (item.pageType === 'host' && item.extra && item.extra.error_ip_list.length) {
        localStorage.setItem('home-host-error-ip-list', item.extra.error_ip_list.join('\n'))
        this.commonGotoPage('bp/?fromhome=1')
      } else if (item.pageType === 'component' && item.extra) {
        this.commonGotoPage(`component/?model=${item.extra.id}`)
      } else if (item.pageType === 'uptimecheck' && item.extra && item.extra.error_task_id_list.length) {
        localStorage.setItem('home-upchecktime-task-id-list', item.extra.error_task_id_list.join(','))
        this.commonGotoPage('uptime_check/?fromhome=1')
      }
    },
    getIconClass(item) {
      let iconType = item.type
      if (item.pageType === 'component' || item.pageType === 'uptimecheck') {
        iconType = this.componentIconMap[item.type] || iconType
      }
      return iconType
    },
    getIconContent(item) {
      return this.iconContentMap[item.type] || item.type
    }
  }
}
</script>

<style scoped lang="scss">
    @import "../common/mixins";

    .title {
      height: 60px;
      width: 100%;
      overflow: hidden;
      font-size: 0;

      @include border-1px();
      .header {
        display: inline-block;
        width: 120px;
        height: 58px;
        font-size: $fontNormalSize;
        text-align: center;
        line-height: 58px;
        background: #f0f1f5;
        color: #6c6e76;
        font-weight: 600;
        border-right: 1px solid $defaultBorderColor;
        float: left;
      }
      .content {
        margin-left: 120px;
        height: 58px;
        background: #fff;
        .canClick {
          color: $primaryColor;
          &:hover {
            cursor: pointer;

            /* stylelint-disable-next-line declaration-no-important */
            color: $primaryHoverColor !important;
          }
        }
        .left-arrow,
        %left-arrow {
          font-size: $fontNormalSize;
          text-align: center;
          margin-left: 15px;
          margin-top: 15px;
          float: left;
          display: inline-block;
          width: 28px;
          height: 28px;
          &:hover {
            cursor: pointer;
            color: #666;
          }
        }
        .right-arrow {
          margin-left: 10px;
          margin-right: 15px;
          float: right;

          @extend %left-arrow;
        }
        .overview-list-wrap {
          overflow: hidden;
          padding: 17px 10px;
          max-width: 1639px;
          .overview-list {
            font-size: $fontSmSize;
            max-height: 24px;
            overflow: hidden;
            margin: 0;
            padding: 0;
            min-width: 2000px;
            .item {
              float: left;
              display: flex;
              flex-wrap: nowrap;
              align-items: center;
              padding: 0 25px;
              min-width: 134.45px;
              &__icon {
                display: inline-block;
                width: 24px;
                height: 24px;
                border-radius: 4px;
                color: #a3c5fd;
                &:hover {
                  cursor: pointer;
                  color: #3a84ff;
                }
              }
              &__abnormal {
                margin-left: 10px;
                color: #de6573;
                font-size: $fontNormalSize;
                &:hover {
                  cursor: pointer;
                }
              }
              &__normal {
                font-size: $fontNormalSize;
              }
            }
            .item-last {
              border-right: 1px solid $defaultBorderColor;
            }
          }
        }

      }
    }
</style>
