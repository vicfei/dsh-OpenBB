# ROADMAP — dsh-OpenBB

北极星：四仓家族的数据基座 + 独立流量面（OpenBB 75k★），30 天目标 100–300★。

## 定位

前三仓（议院/基金会/工作台）缺富数据通道（yfinance 被雅虎全局限流是当日实证）；
OpenBB 多 provider（cboe/sec 免 key，yfinance/fred/polygon 可配）正是解药。
本仓双角色：**独立产品**（目录化桥+研究引擎）+ **家族数据层**（M1 接入三仓数据卡）。

## 里程碑

### M0 ✅（2026-11-16）
桥（目录+一次性执行+provider/时间戳溯源）+ 研究引擎（2 调用模式）。真实冒烟 36s：
NVDA "IV30 年度极值 vs 价格年度低位" 定价悖论；profile 报错路径诚实降级。

### M0.5 · 发布包
- [ ] README 打磨 + 冒烟判决截图首屏 + npm 0.0.1 占位（owner 手动）
- [ ] 公开仓 topics + 四仓互链 + marketplace + 渠道（家族同日）

### M1 · 家族数据层（第 2-3 周）
- [ ] fetch_card --via openbb：三仓数据卡升级为多 provider 富卡（解 yfinance 限流）
- [ ] 目录扩展（ETF/期权链/SEC filings/FRED），provider 探测与降级链
- [ ] REST/OpenAPI 模式（openbb-api 自托管 → DSH agent 全 schema 直驱）

### M2 · 插件化（第 4-6 周）
- [ ] cordis 插件：obb_catalog/obb_run typed tools → `dsh plugin add dsh-openbb`
- [ ] 结果缓存与配额（provider 限速友好）

### M3 · 生态（第 2 月起）
- [ ] 命令目录社区共建 DSL + 数据轨迹标准化（与 RESEARCH-TRAIL 会师）

## 纪律

- 模型不产数（[F#] 挂靠字段）；失败如实报告；provider/时间戳随行；
- 不 vendored 上游代码（Apache-2.0 依赖走 pip）；不做多 key 捆绑。
