# 轻记账（light-ledger）

一款 **不依赖后台** 的纯本地记账微信小程序，基于 **uni-app x + UTS** 开发。
所有数据（账单 / 预算 / 资产 / 发票抬头）仅保存在设备本地存储中，不上传、不联网。

## 目录结构

```
light-ledger/
├── main.uts              # 应用入口
├── App.uvue              # 应用根组件与全局样式
├── manifest.json         # 应用配置（含微信小程序配置）
├── pages.json            # 页面注册 + tabBar（明细/图表/记账/发现/我的）
├── static/tab/           # tabBar 图标（Python 脚本生成的 81x81 PNG）
├── utils/
│   ├── date.uts          # 日期工具（月份切换、星期推算、金额千分位格式化）
│   ├── cats.uts          # 收支分类定义（emoji 图标 + 主题色）
│   └── data.uts          # 数据层（账单/预算/资产/发票的本地存储与统计）
└── pages/
    ├── detail/detail.uvue    # Tab1 明细：月份切换、收支汇总、预算进度、按日分组、删除账单
    ├── chart/chart.uvue      # Tab2 图表：分类排行（进度条）、每日支出趋势（CSS 柱状图）
    ├── record/record.uvue    # Tab3 记账：收/支切换、分类宫格、自定义键盘、备注、日期选择、编辑模式
    ├── discover/discover.uvue# Tab4 发现：月度结余、预算设置、资产管家入口、常用工具
    ├── mine/mine.uvue        # Tab5 我的：记账统计、导出 CSV、存储占用、清空数据、关于
    ├── assets/assets.uvue    # 资产管家：账户增删改、净资产合计
    └── tools/
        ├── mortgage.uvue     # 房贷计算器：等额本息/等额本金
        ├── exchange.uvue     # 汇率转换：内置 8 种常用货币近似汇率
        └── invoice.uvue      # 发票助手：抬头管理、一键复制
```

## 如何运行

1. 用 **HBuilderX 4.41+** 打开 `light-ledger` 目录（uni-app x 工程，编译到微信需 4.41+）。
2. 菜单「运行 → 运行到小程序模拟器 → 微信开发者工具」，首次使用需在 HBuilderX 中配置微信开发者工具安装路径。
3. 编译产物在 `unpackage/dist/dev/mp-weixin`，微信开发者工具打开后即可预览。
4. 未配置 appid 时，在微信开发者工具中使用「测试号」即可本地预览。

## 本地存储 key 约定

| key | 内容 | 格式 |
|---|---|---|
| `ll_bills` | 全部账单 | JSON 数组 `Bill[]` |
| `ll_budgets` | 各月预算 | JSON 对象 `{ "YYYY-MM": number }` |
| `ll_assets` | 资产账户 | JSON 数组 `Asset[]` |
| `ll_invoice` | 发票抬头 | JSON 数组 `Invoice[]` |

> ⚠️ 纯本地存储的限制：数据不能跨设备同步，清除小程序会丢失数据。「我的 → 导出数据」可将账单复制为 CSV 备份。

## 设计说明

- 主色 `#2F6BFF`（品牌蓝），收入绿 `#34C77B`，支出橙/红警示 `#F59E0B`，页面底 `#F7F8FC`
- 分类采用 emoji 图标 + 彩色浅底圆框，无需切图资源
- tabBar「记账」为大加号蓝色圆底图标，突出核心操作
- 全部图表用 CSS 实现（进度条/柱状图），不依赖 echarts，包体更小

## 图标再生成

`static/tab/` 下的图标由 `../icon-gen/gen_icons.py` 生成（纯 Python 标准库，4x 超采样抗锯齿）：

```bash
python icon-gen/gen_icons.py
```
