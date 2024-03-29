<template>
  <panel-card class="use-radio-charts" :title="$t('主机性能状态分布')">
    <div class="sub-title" slot="title"> {{ $t('（数据缓存2mins）') }} </div>
    <div class="radio-content" v-if="options.length">
      <template v-for="(optionList, index) in options">
        <div :key="index" class="radio-content-wrap">
          <div class="chart-item" :class="{ 'item-border': index === 0, 'border-left': !(key % 2) }" v-for="(option, key) in optionList" :key="key">
            <monitor-pie-echart
              class="chart-set"
              chart-type="pie"
              :height="200"
              @chart-click="(e) => handleChartClick(e, option)"
              :options="option">
              <div slot="chartCenter" class="slot-center">
                <div class="slot-center-name" style="width: 56px; text-align: center; font-size: 14px;"> {{ option.name }} </div>
              </div>
            </monitor-pie-echart>
          </div>
        </div>
      </template>
    </div>
  </panel-card>
</template>

<script>
import PanelCard from '../components/panel-card/panel-card'
import { gotoPageMixin } from '../../../common/mixins'
import MonitorPieEchart from '../../../../monitor-ui/monitor-echarts/monitor-echarts'
export default {
  name: 'UseRadioCharts',
  components: {
    PanelCard,
    MonitorPieEchart
  },
  mixins: [gotoPageMixin],
  props: {
    series: {
      type: Array,
      required: true
    },
    showExample: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      colorMaps: {
        '0 ~ 20%': '#a3c5fd',
        '20 ~ 40%': '#699df4',
        '40 ~ 60%': '#3a84ff',
        '60 ~ 80%': '#ffb848',
        '80 ~ 100%': '#ff9c01'
      },
      defaultSerise: [
        {
          data: [
            {
              name: '0 ~ 20%',
              y: 3
            },
            {
              name: '20 ~ 40%',
              y: 4
            },
            {
              name: '40 ~ 60%',
              y: 5
            },
            {
              name: '60 ~ 80%',
              y: 6
            },
            {
              name: '80 ~ 100%',
              y: 7
            }
          ],
          metric_id: 'system.cpu_summary.usage',
          name: 'CPU'
        },
        {
          data: [
            {
              name: '0 ~ 20%',
              y: 3
            },
            {
              name: '20 ~ 40%',
              y: 4
            },
            {
              name: '40 ~ 60%',
              y: 5
            },
            {
              name: '60 ~ 80%',
              y: 6
            },
            {
              name: '80 ~ 100%',
              y: 7
            }
          ],
          metric_id: 'system.cpu_summary.usage',
          name: this.$t('应用内存使用率')
        },
        {
          data: [
            {
              name: '0 ~ 20%',
              y: 3
            },
            {
              name: '20 ~ 40%',
              y: 4
            },
            {
              name: '40 ~ 60%',
              y: 5
            },
            {
              name: '60 ~ 80%',
              y: 6
            },
            {
              name: '80 ~ 100%',
              y: 7
            }
          ],
          metric_id: 'system.cpu_summary.usage',
          name: this.$t('磁盘空间使用率')
        },
        {
          data: [
            {
              name: '0 ~ 20%',
              y: 3
            },
            {
              name: '20 ~ 40%',
              y: 4
            },
            {
              name: '40 ~ 60%',
              y: 5
            },
            {
              name: '60 ~ 80%',
              y: 6
            },
            {
              name: '80 ~ 100%',
              y: 7
            }
          ],
          metric_id: 'system.cpu_summary.usage',
          name: this.$t('磁盘I/O利用率')
        }
      ],
      chartIdMap: {
        [this.$t('CPU使用率')]: 'cpu_usage',
        [this.$t('应用内存使用率')]: 'mem_usage',
        [this.$t('磁盘I/O利用率')]: 'io_util',
        [this.$t('磁盘空间使用率')]: 'disk_in_use'
      }
    }
  },
  computed: {
    options() {
      let data = this.defaultSerise
      if (!this.showExample) {
        data = this.series
      }
      const options = data.map((item) => {
        const itemData = item.data.slice()
        return {
          name: item.name,
          tooltip: {
            trigger: 'item'
          },
          legend: {
            show: true,
            formatter: ['{a|{name}}'].join('\n'),
            right: 20,
            top: 48,
            width: 300,
            icon: 'circle',
            padding: 0,
            textStyle: {
              rich: {
                a: {
                  width: 100,
                  color: !itemData.some(set => set.y > 0) ? '#cccccc' : '#63656E',
                  lineHeight: 25
                }
              }
            }
          },
          series: [{
            type: 'pie',
            radius: ['55%', '70%'],
            left: -260,
            avoidLabelOverlap: false,
            label: {
              show: false,
              position: 'center'
            },
            labelLine: {
              show: false
            },
            data: itemData.sort((a, b) => +a.name.slice(0, 1) - +b.name.slice(0, 1)).map((set) => {
              const itemColor = Math.abs(set.y) > 0 ? this.colorMaps[set.name] : '#cccccc'
              return {
                name: set.name,
                value: set.y,
                ...set,
                itemStyle: {
                  color: itemColor
                },
                tooltip: {
                  formatter: () => `<span style="color:${itemColor}">\u25CF</span> <b> ${set.name}</b>
                  <br/>${item.name}: <b><span style="color:#FFFFFF">${set.y}</span>${this.$t('台')}</b><br/>`,
                  textStyle: {
                    fontSize: 12
                  }
                }
              }
            })
          }]
        }
      })
      return options.reduce((pre, cur, index) => {
        index % 2 ? pre[0].push(cur) : pre[1].push(cur)
        return pre
      }, [[], []])
    }
  },
  methods: {
    gotoPerformace(target) {
      // agent状态默认为正常
      this.$router.push({
        name: 'performance',
        params: {
          search: [target, {
            id: 'status',
            value: [0]
          }]
        }
      })
    },
    handleChartClick(params, option) {
      if (params.data.ip_list && params.data.ip_list.length) {
        const scopes = params.name.replace(/\s+/g, '').replace('%', '')
          .split('~')
        this.gotoPerformace({
          id: this.chartIdMap[option.name],
          value: [
            {
              condition: '>=',
              value: scopes[0]
            },
            {
              condition: '<=',
              value: scopes[1]
            }
          ]
        })
      }
      return false
    }
  }
}
</script>

<style scoped lang="scss">
    @import "../common/mixins";

    .use-radio-charts {
      .sub-title {
        color: #999;
        font-size: 12px;
        line-height: 20px;
      }
      .content {
        display: flex;
        align-items: center;
        justify-content: space-around;
        flex-wrap: wrap;
        &-chart {
          padding: 20px 0;
          position: relative;
          width: 40%;
          z-index: 1;

          @media only screen and (max-width: 1882px) {
            .slot-center {
              left: 97px;
            }
          }
          .slot-center {
            position: absolute;
            left: 47px;
            top: 55px;
            width: 56px;
            height: 38px;
            font-size: $fontSmSize;
            color: $defaultFontColor;
            line-height: 19px;
            text-align: center;
            z-index: 1;
          }
          &-no-data {
            width: 125px;
            height: 125px;
            background: #fff;
            border-radius: 100%;
            z-index: 888;
            position: absolute;
            left: 32px;
            top: 30px;
            border: 12.5px solid $defaultBorderColor;
            .name {
              width: 56px;
              height: 38px;
              font-size: $fontSmSize;
              color: $defaultFontColor;
              line-height: 19px;
              text-align: center;
              position: absolute;
              left: 22px;
              top: 31px;
            }
          }
        }
        &-border {
          height: 160px;
          width: 0px;
          border: .5px solid #ddd;
        }
        .border-b {
          border-bottom: 1px solid #ddd;
        }
      }
      .radio-content {
        display: flex;
        flex-direction: column;
        margin: 0 -20px;
        &-wrap {
          display: flex;
          align-items: center;
          .chart-item {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            &.item-border {
              &::after {
                position: absolute;
                left: 60px;
                right: 60px;
                bottom: 0px;
                content: " ";
                height: 1px;
                background: rgb(221, 221, 221);
              }
            }
            &.border-left {
              &::before {
                position: absolute;
                top: 20px;
                bottom: 20px;
                right: 0px;
                content: " ";
                width: 1px;
                background: #ddd;
                z-index: 99;
              }
            }
            .chart-set {
              flex: 0 0 516px;
              width: 516px;
              min-width: 516px;
              max-width: 516px;
              position: relative;
              .slot-center {
                position: absolute;
                left: -157px
              }
            }
          }
        }
      }
    }
</style>
