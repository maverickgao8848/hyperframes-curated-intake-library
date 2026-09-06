# Curated Intake 精简改造方案

状态：阶段 A–F 全部完成；全仓回归、Skill 验证、库验证与真实 v3 staging 回归通过
范围：组件库归位、Building Block 说明与分类、精简路由、精简 Storyboard、历史文档清理

## 1. 核心判断

本次改造不把 Curated Intake 扩展成完整的视频编译器。它只负责在构建前确认素材范围、选择 Frame、形成可执行的镜头方案、绑定真实可复用资源，并把结果交给 HyperFrames。

改造遵循四条原则：

1. 组件目录详细，Storyboard 简单。
2. 后台验证严格，导演表达轻量。
3. 只有会改变用户决定、成片结果或验证结果的信息才进入合同。
4. Video Spec Builder 提供镜头拆分和组件说明方面的参考，但不直接复制其全部字段。

## 2. 明确保留与明确删除

保留：

- Building Blocks 随 Skill 分发，不再依赖仓库根目录的共享 Content/Library 位置。
- 每个重要视觉组件都有用途、适用条件、禁用条件、内容要求和运动能力说明。
- 用户批准的组件、Logo、SVG、Lottie 和真实素材使用精确 catalog ID。
- license、hash、provenance、installability、staging receipt 和 approval 等生产约束。
- 镜头级时间范围、画面、运动和场间衔接。

删除或不再引入：

- 多轴认知分类和复杂导演评分模型。
- 强制 Building Block 与 Motion Recipe 配对。
- Scene → Shot → Beat → Event 多层合同。
- 场景级 `takeaway`。
- `visual_thesis.subject/change/semantic_bridge` 三段式对象。
- `focus.primary/secondary`。
- Storyboard 中的 CSS selector、事件百分比窗口和逐事件 role/purpose。
- 在多个文件中重复同一创意决定。

## 3. 组件库归位

### 3.1 目标位置

```text
.agents/skills/hyperframes-curated-intake/
├── SKILL.md
├── agents/
├── references/
├── scripts/
└── assets/
    └── library/
        ├── catalog.json
        ├── components/
        ├── registry/
        │   ├── registry.json
        │   ├── blocks/
        │   ├── components/
        │   └── assets/
        ├── media/
        ├── frames/
        ├── previews/
        ├── licenses/
        └── provenance/
```

`components/` 是 canonical source；`registry/` 是由 source 和 catalog 生成的安装投影。人工修改只能发生在 canonical source，不能直接修改生成投影。

### 3.2 路径规则

脚本默认从 `skill_root/assets/library` 读取组件库，同时保留显式 `--library` 参数用于测试或外部库。

迁移顺序：

1. 将现有库复制到 Skill assets。
2. 修改默认路径、README、Schema 和测试。
3. 重建 catalog、registry、legacy aliases、hash 和 provenance。
4. 验证 staging 后的项目文件及哈希与迁移前一致。
5. 确认没有调用方依赖根目录 `library/` 后，再移除旧位置。

迁移期间不能长期保留两个 canonical library。

## 4. Building Block 最小导演合同

机器 `kind` 继续表示接入方式，例如 `registry-block`、`registry-component`、`svg`、`logo`、`lottie`、`transition`。

需要导演判断的视觉 Block/Component 使用以下最小字段：

```yaml
family: process
purpose: 展示一个过程如何逐步推进
useWhen:
  - 3–5 个线性步骤
  - 需要突出当前进度
avoidWhen:
  - 存在明显分支
  - 节点超过 6 个
expects:
  - 步骤名称
  - 当前步骤
  - 可选节点指标
motion: progressive
fallbackIds:
  - registry-component:flow-complex
  - registry-component:flow-branching
```

只保留六项导演信息：

- `family`
- `purpose`
- `useWhen`
- `avoidWhen`
- `expects`
- `motion`

`fallbackIds` 仅在存在明确近邻组件时填写。

### 4.1 主分类

每个视觉组件只有一个主分类：

1. `data`：数据、趋势、比例、排名。
2. `process`：步骤、流程、分支、循环。
3. `structure`：层级、关系、网络、分类。
4. `compare`：对比、筛选、决策。
5. `interface`：软件界面、终端、对话、操作。
6. `concept`：抽象概念、机制、类比。
7. `emphasis`：大字、数字、引用、关键词。
8. `evidence`：Logo、截图、文档、真实引用。

不再为同一组件同时维护多套叙事角色、认知动作和运动语法分类。

### 4.2 运动等级

- `entrance-only`：主要只有入场、停留和退场。
- `progressive`：能够按步骤持续推进。
- `stateful`：能够发生筛选、分支、变形或状态转换。

该字段只用于避免长镜头误选只能入场一次的静态组件，不扩展为独立 Motion Recipe 路由系统。

### 4.3 单一事实源

导演说明写入机器可读的 catalog/item metadata，再由脚本生成供人阅读的 Building Block Catalog。不得同时手工维护 JSON 与一份内容重复的组件 Markdown 目录。

Logo、字体、SFX 等明确身份资源不需要强行补写完整导演说明；它们只需要身份、用途范围、格式、来源、许可和接入信息。

## 5. 精简路由

路由只做三件事：

1. 根据当前镜头需要的画面，从 `family + purpose + useWhen` 找到候选。
2. 使用 `avoidWhen + expects + motion` 排除明显不适合的候选。
3. 执行 readiness、license、required inputs、aspect、duration 和 installability 硬过滤。

附加规则：

- 用户明确指定的可用组件或素材直接锁定，不重新评分替换。
- 明确指定的 Logo/SVG 按 ID 直接绑定，不经过语义路由。
- 长于约 3 秒的镜头优先使用 `progressive` 或 `stateful` 组件。
- 没有合适项时记录 catalog miss，不用无关组件凑数。
- 重复使用只做轻量惩罚，不设置复杂配额。

候选、过滤结果和来源记录在内部 curation state；Storyboard 只记录最终选择。

## 6. 精简 Storyboard

### 6.1 单层镜头模型

Storyboard 中一条 Scene 就是一条可剪辑镜头，不再新增 Shot、Beat 或 Event 子层。需要章节结构时使用 Markdown 分组，不新增机器层级。

每镜核心结构：

```markdown
### S01 · 0.0–2.0s

- 内容：从 20 个候选中只留下真正相关的 3 个
- 画面：文件流经过扫描区，不合格文件变灰掉落，3 个文件继续向前
- 使用：registry-component:flow-complex、svg:document
- 运动：文件持续流入 → 逐个判断 → 淘汰项掉落 → 结果汇合
- 下一镜：3 个文件折叠成下一镜的三层结构
```

核心信息只有：

- 稳定镜头 ID 和起止时间；
- `内容`；
- `画面`；
- `使用`；
- `运动`；
- 到下一镜的衔接。

以下字段按需填写，不作为每镜必填项：

- 旁白；
- 屏显文案；
- 音效；
- 来源锚点；
- 特殊用户锁。

普通硬切可以省略“下一镜”。最后一镜允许没有衔接。

### 6.2 防止幻灯片感的两条规则

1. 镜头超过约 3 秒时，必须存在一次以上内部语义变化，或明确说明为什么需要静止。
2. “标题出现、卡片出现、整体淡出”不能单独构成完整运动设计。

不通过强制事件数量、CSS selector 或时间百分比来保证动感。

### 6.3 从 Video Spec Builder 保留什么

保留：

- 一个记录对应一个镜头；
- 明确起止时间；
- 明确画面、组件、运动和场间切换；
- 镜头时长有快慢变化；
- 长镜头必须解释其信息或运动承载。

不保留：

- 每镜固定 11 个字段；
- `期待内容`、`期待效果`、场景级 takeaway 等重复描述；
- 同时填写“转场进入”和上一镜“转场离开”；
- Storyboard 与音频时间轴重复音效细节；
- 强制每镜填写无意义的“无”。

## 7. Curated Intake 原有优势

以下能力不得因精简 Storyboard 而退化：

- 精确 catalog ID；
- Logo/SVG/Lottie/真实素材绑定；
- 用户批准和显式锁；
- Frame 选择和素材范围确认；
- source-preserve；
- license、hash、provenance；
- staging receipt；
- render-time network 禁止；
- catalog miss；
- Storyboard 作为唯一镜头级创意权威。

这些生产信息不全部出现在 Storyboard 中，而由 catalog、curation、manifest 和 receipt 分别拥有。

## 8. 实施顺序

### 阶段 A：建立基线

- 保存当前测试结果和库清单。
- 梳理根目录 `library/` 的所有调用方。
- 确认当前未提交改动的归属，避免覆盖已有 v2 工作。

### 阶段 B：组件库归位

- [x] 创建 Skill assets library。
- [x] 切换默认路径和调用方。
- [x] 重建派生产物并验证哈希、Registry 和 staging。
- [x] 更新 README 的仓库结构说明，并在完整恢复归档验证后移除根 `library/` 镜像。

### 阶段 C：Catalog 最小导演字段

- [x] 更新 library schema：revision 14 条件合同已定义；revision 13 保留为迁移输入。
- [x] 更新 service tooling：保留并逐值投影六项导演 metadata，提供非写入迁移报告，并为 revision 14 增加合同验证。
- [x] 为 48 个 Registry Block 和 123 个 Registry Component 逐项补齐六项导演信息。
- [x] 为 31 个 SVG 和 30 个 Lottie 逐项补齐六项导演信息。
- [x] 为 111 个轻量资产保持既有合同，不复制导演字段。
- [x] 从 catalog 确定性生成 Registry 与可阅读 director catalog 投影。

### 阶段 D：精简路由

- [x] 定义 revision 15 单一六字段 routing 与无数值权重 curation audit；revision 14 保留为 migration input。
- [x] 用 family → useWhen → purpose 三步语义路由替换分类和数值权重；后续只按长镜头 motion、prior-use、ID 破同层平局。
- [x] 将 canonical 一次迁移到 revision 15，移除旧决策字段并确定性重建投影；revision 14 仅保留为显式 migration input。
- [x] 保留生产硬过滤、显式锁、声明顺序 fallback 和 catalog miss。
- [x] 对中英文内容使用结构化字段，不依赖少量英文关键词。

### 阶段 E：精简 Storyboard

- [x] E1 types：定义 canonical `hyperframes-storyboard/v3` 单层镜头 Schema、v3 routed patch 与纯 timing/next/uses/locks 验证合同。
- [x] 将原 v2 Schema 原样冻结到唯一 `storyboard-spec.v2.legacy.schema.json`，仅供显式 migration 使用。
- [x] 编写确定性 v2→v3 迁移器；input/output/report 必填且互异，迁移只生成 draft 与外置 needs-review 报告，不继承 approval/locks。
- [x] 将 standalone/routed handoff、parser、renderer、selector、staging、verification、fixtures 和测试切换到 v3-only；v2 生产输入 fail-fast 指向迁移命令。
- [x] E3 production cleanup：移除最后的 v2 request/compiled adapter；保留显式 v2→v3 migration、frozen v2 Schema/测试/历史，并以 canonical rev15 完成仓库外真实 v3 routed/staging 回归。

### 阶段 F：清理与回归

- [x] 删除被本方案取代的历史规格和临时调查文档。
- [x] F1：删除零 consumer 的 routed-result v2 legacy Schema 与 stale revision 7 inventory provenance；保留 frozen Storyboard v2 Schema 与显式 v2→v3 migrator。
- [x] 清除其余死 Schema、死脚本、重复 catalog 投影和无调用引用；保留有活动用途的 Registry、director catalog 与唯一 current inventory 投影。
- [x] 执行仓库单元测试、Skill 验证、库验证和一个真实项目 staging 回归。

## 9. 验收标准

- Skill 在不依赖仓库根目录 `library/` 的情况下完成选材和 staging。
- 每个可路由视觉组件都有最小导演说明。
- 同类组件能依据 `useWhen/avoidWhen/expects` 被区分。
- 长镜头不会默认选择 `entrance-only` 组件作为唯一运动主体。
- Storyboard 不要求 takeaway、visual thesis 对象、focus、selector 或事件百分比。
- 用户指定的 Logo/SVG/组件在 handoff 和 staging 中不丢失。
- Storyboard 中一个镜头只描述一次转场。
- 不存在两个互相竞争的 canonical library 或改造规格。

## 10. 历史开发文档清理建议

以下判断基于当前引用扫描；执行删除前仍需做一次最终全仓引用检查。

### 10.1 保留并纳入版本控制

- `AGENTS.md`：当前仓库协作与精简约束，属于有效指令。
- `README.md`：仓库入口；组件库迁移后需要更新目录说明。
- `CONTRIBUTING.md`：有效协作说明。
- `docs/library-provenance/talkcraft-partner-authorization.md`：资产授权证据，不能删除。
- 本文档：确认后作为本轮唯一改造方案。

### 10.2 已清理的历史文档

以下未跟踪文档已由用户确认并删除；仍有效的决策已经收敛到本文：

- `CURATED-INTAKE-V2-REFACTOR-SPEC.md`
- `docs/video-spec-builder-hyperframes-refactor-plan.md`
- `docs/motion-skill-comparison-2026-09-04.md`
- `HYPERFRAMES_DIRECTED_VIDEO_SKILL_SPEC.md`

### 10.3 已核对并清理

- `HYPERFRAMES_VISUAL_DIRECTOR_SKILL_SPEC.md`：实现前规格已被正式 `hyperframes-visual-director` Skill、Schema、脚本和测试覆盖；其中保留 Beat/Event/scene-contract 的旧 Curated 设计与本方案冲突，已删除以避免平行权威。
- `allocate-beats.py`、`verify-beats.py`：无活动调用方，并与 Storyboard v3 单层合同冲突，已删除。
- `migrate-storyboard-v1-to-v2.py`：无活动调用方，会重新生成已淘汰的 v2 selector/event 结构；生产迁移只保留受测的 v2→v3 显式入口。

### 10.4 不应当作“开发文档”直接删除

- `video-spec.md` 与 `videos/video-spec-builder-promo/`：两者相互引用，是演示项目而非普通设计文档。若需要长期维护，应整体迁移到 `examples/`；若不需要该演示，则应连同整个演示目录一起删除，不能只删根部 spec。
- `video-spec-builder/`：这是完整的外部 Skill 源副本，不只是文档。组件迁移和规则抽取完成后，再决定将其作为明确的 vendor/reference 保留，或整体移除；不应零散删除其中 README 和 references。

## 11. 非目标

- 不在本轮重做 HyperFrames Builder。
- 不新增视频工作台。
- 不建立复杂 Motion Recipe 编排系统。
- 不将 Curated Intake 变成音频、字幕或渲染器。
- 不为了兼容未使用的历史文档保留双套 Schema。

## 12. Evaluation Log

| 阶段 | 实现状态 | 验收状态 | 证据 |
| --- | --- | --- | --- |
| A | 完成 | 已作为 B 的冻结输入 | `docs/curated-intake-lean-refactor-baseline.md` 记录初始工作树、测试、调用方和 manifest |
| B1 | 完成 | PASS | canonical Skill library 复制与逐文件校验 |
| B2 | 完成 | PASS within baseline | 默认事实源、调用方、文档和测试切流 |
| B3 | 完成 | PASS | pinned TalkCraft clean-room、确定性派生、staging 和 source/root 保护证据 |
| B4 | 完成 | PASS | 根镜像可恢复归档、受控删除、零活动调用方和 canonical 回归证据 |
| C1 types | 完成 | PASS | revision 14 条件 Schema、revision 13 canonical-valid 和严格 fixture tests |
| C2 service | 修订完成 | PASS | 七字段原样只读、互斥 `--check/--report`、库内报告拒绝、revision 14 verifier 与 legacy 路由不变回归 |
| C3 catalog | 完成 | PASS | 232 项逐项语义策展、revision 14、双 clean-room 确定性、派生投影与保护审计 |
| D1 types/contracts | 完成 | PASS | revision 15 七字段-only routing、无权重 candidate audit、revision 14 migration input 与 Storyboard hash guard |
| D2 runtime | 最小修订完成 | PASS | 六字段 lexicographic 路由、v5 audit、完整 catalog Schema 预检、Schema 派生且 fail-closed 的 integration 门禁、显式锁/fallback、semantic Hero、TalkCraft passthrough |
| D3 catalog migration | 完成 | PASS | rev14→15 一次迁移、4,778 个旧决策字段移除、10 项机器事实显式化、双 clean-room 确定性与 selector/派生回归 |
| E1 Storyboard types | 最小修订完成 | PASS | v3 单层 Schema、与根 Library Schema kind enum 完全一致的 uses namespace、严格 next/locks、连续时间纯验证、v3 patch lock 合同与 frozen v2 guard |
| E2 migration/runtime | rubric 最小修订完成 | PASS | Schema/runtime 所有 production boundary 仅接受 exact `motion-attestation/v1` 并回报 actual+supported；agent attestation 与 live recipe provenance 其余冻结 |
| E3 production cleanup | 最小修订完成 | PASS | production routed request/compiled/result 均为 v3；最小 fixture 与仓库外 canonical rev15 闭环通过 |
| F1 bounded cleanup | 完成 | PASS | 精确删除零 consumer routed-result v2 Schema 与 stale rev7 inventory provenance；`inventory-latest.json` 唯一 current；三 Skill output boundary 合同回归 |
| F2 regression + approved test migration | 完成 | PASS | 原四项改为当前 v3 的 8 Frame 全量 staging、media/handoff hash、输出边界、namespace/integration/stageability 与 unknown-use fail-closed 回归 |
| F3 final cleanup | 完成 | PASS | 删除冲突的实施前规格、Beat/Event 死 CLI、无 consumer 的 v1→v2 生成器及其死 helper；全仓 273 tests passed，Skill quick validation、library contract、只读 refactor check、compileall 与 diff check 通过 |
