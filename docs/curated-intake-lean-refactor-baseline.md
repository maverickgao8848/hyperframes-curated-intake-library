# Curated Intake 精简改造基线（Sprint A）

本文件冻结组件库归位前的仓库、测试、库清单和工作树边界。后续阶段必须以这里记录的基线做迁移核对，不得把本轮开始前已经存在的用户 / v2 工作误认为 Sprint A 产物。

## 1. 仓库快照

| 项目 | 基线值 |
| --- | --- |
| workspace | `C:/Users/buend/Desktop/mav 3` |
| branch | `codex/fix-curated-intake-v2-promo-motion` |
| HEAD | `b56c9d4f4fe5b59082ae146a347a69a7d565346c` |
| 记录时间 | `2026-09-04T22:10:40+08:00` |
| 工作树 | dirty；详见第 5 节 |
| 根组件库 | Sprint A 历史快照：`library/` 当时存在；已在 B4 归档后移除 |
| Skill 内目标库 | Sprint A 历史快照：当时 **missing**；B1 起已成为 canonical |

Sprint A 只新增本文件。第 5 节列出的 `M`、`D`、`??` 路径在本轮开始前均已存在，归属用户 / v2 工作；Sprint A 不修改、恢复、删除、格式化或重新生成它们。

## 2. 测试基线

测试结果是迁移前已记录的现状，不把现有失败归因于 Sprint A。以下两条命令已在本基线工作树实际执行。

| 测试集合 | 正确路径 | 结果 | 归因 |
| --- | --- | --- | --- |
| Curated Intake 四文件合跑 | `tests/unit/test_curated_intake_workflow.py`；`tests/unit/test_curated_routed_mode.py`；`tests/unit/test_library_routing_contract.py`；`tests/unit/test_video_spec_handoff_refactor.py` | exit code **1**；passed **13**；failed **4**；skipped **0**；errors **0** | 4 个失败全部位于 video-spec handoff 范围 |
| 全部 unit tests | `tests/unit` | exit code **1**；passed **30**；failed **4**；skipped **0**；errors **0** | 4 个失败全部位于 `tests/unit/test_video_spec_handoff_refactor.py` |

```powershell
python -m pytest tests/unit/test_curated_intake_workflow.py tests/unit/test_curated_routed_mode.py tests/unit/test_library_routing_contract.py tests/unit/test_video_spec_handoff_refactor.py
python -m pytest tests/unit
```

两条命令报告相同的 4 个完整失败 node ID：

1. `tests/unit/test_video_spec_handoff_refactor.py::VideoSpecHandoffRefactorTests::test_all_eight_inventory_frames_materialize_byte_exact`
2. `tests/unit/test_video_spec_handoff_refactor.py::VideoSpecHandoffRefactorTests::test_handoff_validates_media_and_writes_only_thin_compatibility_brief`
3. `tests/unit/test_video_spec_handoff_refactor.py::VideoSpecHandoffRefactorTests::test_template_is_upstream_only`
4. `tests/unit/test_video_spec_handoff_refactor.py::VideoSpecHandoffRefactorTests::test_unknown_media_reference_fails_closed`

阶段 B 的回归比较规则：不得新增失败；现有 4 个 handoff 失败应保持为已知基线问题，除非后续阶段的明确合同负责修复它们。不能用错误的旧测试路径替代上表四个路径。

## 3. 根 `library/` 确定性基线

### 3.1 规模与完整性

| 指标 | 基线值 |
| --- | ---: |
| 文件数 | 1,576 |
| 总字节数 | 52,862,307 |
| catalog entries | 356 |
| registry items | 162 |
| frames | 8 |
| inventory errors | 0 |
| inventory warnings | 19 |
| duplicate hash groups | 184 |
| duplicate files | 890 |
| largest duplicate group | 117 |

`library/inventory-latest.json` 的 catalog 摘要还记录：revision `13`、ready `347`、disabled `9`、registry eligible / mapped / valid 均为 `162`。19 个 warning 属于迁移前基线，阶段 B 不得静默增加、丢弃或重解释。

规模、重复项和关键文件哈希可在仓库根目录用 PowerShell 复算；这里只保存汇总，不复制 1,576 条文件记录：

```powershell
$libraryFiles = Get-ChildItem -LiteralPath 'library' -File -Recurse
$hashGroups = $libraryFiles | Get-FileHash -Algorithm SHA256 | Group-Object Hash
[pscustomobject]@{
  files = $libraryFiles.Count
  bytes = ($libraryFiles | Measure-Object Length -Sum).Sum
  duplicateHashGroups = @($hashGroups | Where-Object Count -gt 1).Count
  duplicateFiles = ($hashGroups | Where-Object Count -gt 1 | Measure-Object Count -Sum).Sum
  largestDuplicateGroup = ($hashGroups | Measure-Object Count -Maximum).Maximum
}
Get-FileHash -Algorithm SHA256 -LiteralPath 'library/catalog.json','library/registry/registry.json','library/inventory-latest.json'
```

inventory 可由当前脚本显式指定根库后复算（阶段 B 切换为 Skill 内库路径）：

```powershell
python .agents/skills/hyperframes-curated-intake/scripts/inventory-library.py --library library --output library/inventory-latest.json
```

### 3.2 关键 SHA-256

| 文件 | SHA-256 |
| --- | --- |
| `library/catalog.json` | `5b022cd3ee07ee7efb90faf676cbb340daec65247a859fdd618561dd2064c8f2` |
| `library/registry/registry.json` | `e9e643262315e583948965f7275f10a0a984e8bcfe7303269505d1f0397ef1e2` |
| `library/inventory-latest.json` | `d147f8faca478fe4284397d2222df31b8329b3610cce765a51e64b5a015a7fea` |

### 3.3 逐项迁移事实源

`library/inventory-latest.json` 是阶段 B **唯一的逐项清单事实源**。迁移不能只比较总文件数或目录大小；必须逐项核对其中的：

- catalog entry ID、kind、status；
- 每个 `sourceFiles[].path` 的存在性、SHA-256 和 `hashMatches`；
- preview 路径与存在性；
- registry 映射和 registry item 总数；
- 8 个 Frame 的 preset、路径和 SHA-256；
- errors / warnings 集合。

阶段 B 复制完成后，应从 Skill 内新库重新生成 inventory，并以本文件记录的 `library/inventory-latest.json` 及其 SHA 作为迁移输入快照进行逐项比较。catalog、registry 和 inventory 的关键 SHA 只有在明确的生成步骤需要改变内容时才允许变化；变化必须能追溯到后续 Sprint 的合同和生成记录。

## 4. 根 `library/` 调用方矩阵

“目标”表示后续阶段完成后应指向的位置或应保持的行为；本 Sprint 不执行这些迁移。

| 分类 | 当前调用方 / 引用 | 当前依赖 | 后续阶段 | 目标 |
| --- | --- | --- | --- | --- |
| 默认路径解析 | `.agents/skills/hyperframes-curated-intake/scripts/_registry.py` | `default_library()` 通过 `parents[4] / "library"` 指向仓库根库 | B | 改为相对 Skill 根的 `assets/library`；继续允许显式 `--library` 覆盖 |
| 默认路径消费者 | `.agents/skills/hyperframes-curated-intake/scripts/inventory-library.py`；`build-registry-view.py` | 默认调用 `_registry.default_library()` | B | 默认使用 Skill 内库；外部库测试仍可传 `--library` |
| 必填 CLI 库消费者 | `select-project-palette.py`；`prepare-project.py`；`stage-selected-items.py` | `--library` 必填，并从传入库读 catalog / registry / source files | B | Skill 工作流默认传 Skill 内库；保留显式参数用于测试和外部库 |
| catalog / registry 读取核心 | `_curation.py`；`_registry.py` | 从给定 library 读取 `catalog.json`，并解析 source / registry | B | 路径无仓库根假设；canonical 数据来自 Skill 内库 |
| v2 路由与迁移工具 | `apply-video-spec-refactor.py`；`build-director-catalog.py`；`build-legacy-aliases.py`；`verify-legacy-registry.py`；`verify-library-contract.py` | 显式 `--library`；读取 catalog、director catalog、registry 或 aliases | B/C/D/E | 所有命令以 Skill 内库为生产目标；测试临时库继续可注入 |
| 派生 metadata | `build-legacy-aliases.py` 生成内容中的 `source: library/catalog.json`；`inventory-library.py` 生成内容中的 `library: "."` | 记录旧逻辑路径或库内相对路径 | B | provenance 使用可迁移、以库根为基准的相对路径；不得把仓库根写成新的事实源 |
| Curated Intake 操作文档 | `.agents/skills/hyperframes-curated-intake/SKILL.md` | 示例显式要求 `<library>` | B | 明确默认库为 `assets/library`，并说明 `--library` 仅为覆盖入口 |
| Curated Intake 路由文档 | `.agents/skills/hyperframes-curated-intake/references/library-routing.md` | 文案把 `library/catalog.json` 写为路由权威 | B/D | 表述为 Skill 内 `assets/library/catalog.json`；仍保持 catalog 为唯一路由权威 |
| Brief Controller | `.agents/skills/hyperframes-brief-controller/SKILL.md`；`references/brief-contract.md` | 直接引用根库 frames 和 registry | B | 指向 Curated Intake Skill 内库，或通过明确接口解析；禁止复制第二 canonical library |
| Visual Director | `.agents/skills/hyperframes-visual-director/SKILL.md` | 直接引用 `library/director-catalog.json` | B/C | 指向 Skill 内生成的 director catalog；保持其为 catalog 投影而非第二事实源 |
| Visual Director inventory：库参数边 | `.agents/skills/hyperframes-visual-director/scripts/inventory-library.py` | 必填 `--library`，将参数解析为写入和读取库根 | B | 保留显式注入；生产调用传 Curated Intake Skill 内库 |
| Visual Director inventory：写边 | `.agents/skills/hyperframes-visual-director/scripts/inventory-library.py` | 写入 `<library>/talkcraft-inventory.json` | B/C | 写入 Skill 内 canonical library；写后由 inventory / provenance 验证 |
| Visual Director inventory：生成器调用边 | `.agents/skills/hyperframes-visual-director/scripts/inventory-library.py` | 调用 Curated Intake 的 `build-director-catalog.py --library <library>` | B/C | 继续单一路径生成，但 `<library>` 必须是 Skill 内库 |
| Visual Director inventory：读边 | `.agents/skills/hyperframes-visual-director/scripts/inventory-library.py` | 读取 `<library>/director-catalog.json` 并汇报条目数 | B/C | 读取刚由同一 Skill 内库生成的投影，不允许回落到根库 |
| 真实根库合同测试 | `tests/unit/test_library_routing_contract.py` | `ROOT / "library"`；校验 catalog、director catalog、legacy registry | B/C/D | 改为 Skill 内库路径，并继续验证生成投影无漂移 |
| 真实根库 handoff 测试 | `tests/unit/test_video_spec_handoff_refactor.py` | `ROOT / "library"`；读取 Frame inventory / 文件并传 `--library` | B/E | 改为 Skill 内库；保留逐字节 staging 断言 |
| 其他真实根库测试 | `tests/unit/test_talkcraft_director_inventory.py`；`tests/unit/test_visual_director_block_candidates.py` | 读取根 `director-catalog.json` 或 `catalog.json` | B/C/F | 切到 Skill 内库，继续验证 downstream 投影和候选兼容性 |
| 临时库单元测试 | `tests/unit/test_curated_intake_workflow.py`；`tests/unit/test_curated_routed_mode.py` | 在临时目录创建 library 并显式传参 | B/F | 保持注入式临时库，不应改成依赖生产库 |
| 传统临时库测试 | `tests/test_curated_inventory_library.py`；`tests/test_curated_registry_view.py` | 在临时目录创建 library 并显式传参 | B/F | 保持隔离测试；只更新默认路径断言（若有） |
| 仓库结构说明 | `README.md` | 宣称根 `library/` 是完整共享库 | B/F | 改为 Skill 内库结构，确认无调用方后删除旧根库说明 |
| 资产贡献规则 | `CONTRIBUTING.md` | 以 `library/` 表示受版本控制资产边界 | B/F | 指向 Skill 内库并保留许可要求 |
| Schema | `schemas/library.schema.json` | 定义 catalog schema，不是路径消费者 | C | Schema 随 canonical library 放置策略更新；避免复制成两个权威版本 |

补充边界：项目 staging 后出现的 `assets/library/...` 与 `compositions/.../library/...` 是项目内安装目标，不是根 canonical library 调用方，不应在阶段 B 被误改为 Skill 源路径。

### 4.1 `source-provenance.json` 的 candidate 路径边

`docs/library-provenance/source-provenance.json` 中共有且仅有以下 3 条 `library/candidates/...` 引用。三者文件当前均存在，实际 SHA-256 与 provenance 记录一致；相同字节也已投影到对应 `library/registry/blocks/...` 文件。它们不是可丢弃的历史文本：当前 `catalog.json` 仍把 candidate 文件列为 bundle source / preview，因此 B1 必须原样复制，不能只复制 registry 投影。

| ID | provenance 引用 | SHA-256 | 分类 | 后续处置 |
| --- | --- | --- | --- | --- |
| `registry-block:wechat-desktop-exchange` | `library/candidates/visual-director/blocks/wechat-desktop-exchange.html` | `2e3e19eb5136aac03266603cda2c1620e0539e88332ac92d0ed0ab084a5a3b6e` | 活跃 candidate source；registry 为派生投影 | B1 原样复制到 Skill 内库同相对路径；B2 将 provenance 的仓库相对路径改为 `.agents/skills/hyperframes-curated-intake/assets/library/candidates/visual-director/blocks/wechat-desktop-exchange.html`；C 才能决定是否归位到 canonical `components/`，并同步 catalog / provenance / registry 生成链 |
| `registry-block:chatgpt-desktop-exchange` | `library/candidates/visual-director/blocks/chatgpt-desktop-exchange.html` | `423b15cf433ae6cd480526ecc0e2dadfcf76e9cf87c6eff153affdb5c50070f6` | 活跃 candidate source；registry 为派生投影 | B1 原样复制到 Skill 内库同相对路径；B2 更新 provenance 路径；C 才能连同 catalog source / preview 一起归位，禁止提前删除 candidate |
| `registry-block:film-credits-stagger` | `library/candidates/visual-director/blocks/film-credits-stagger.html` | `f75373b3c36fd1acc1e862105fd161b452a840a08bcc30ce15c6b6407e03f93f` | 活跃 candidate source；registry 为派生投影 | B1 原样复制到 Skill 内库同相对路径；B2 更新 provenance 路径；C 才能连同 catalog source / preview 一起归位，禁止提前删除 candidate |

### 4.2 阶段 B dirty 文件合并策略

下表只列阶段 B 会修改、移动、删除或作为 B1 复制输入读取，且当前为 dirty 的路径。`manual-preserve` 表示只在当前工作树内容上做最小路径补丁，先后对比并保留既有 v2 语义；`unresolved` 表示尚无证据证明可以移动、删除或把未提交内容固化为新 canonical source，因此不能执行该动作。

去重计数汇总：`manual-preserve` **7** 个文件；`unresolved` **103** 个文件（其他文件 **14** + 展开的 registry 文件 **89**）；阶段 B 涉及的 dirty concrete files 合计 **110**。下表中的 13 条 registry directory rows 仅用于呈现 Git 折叠分组，**不作为 concrete files 重复计数**；其成员以随后展开的 89 条文件记录为准。

| 当前状态 | 路径 | B 中角色 | merge strategy / 授权状态 |
| --- | --- | --- | --- |
| M | `.agents/skills/hyperframes-curated-intake/SKILL.md` | 更新默认库和命令说明 | `manual-preserve`：仅改库路径/默认值说明，保留全部现有 v2 内容；修改前后逐段 diff |
| ?? | `.agents/skills/hyperframes-curated-intake/references/library-routing.md` | 更新唯一路由权威路径 | `unresolved`：未跟踪文件的纳入与改写授权未被单独证实；B2 前需确认 |
| M | `.agents/skills/hyperframes-curated-intake/scripts/_registry.py` | 切换 `default_library()` | `manual-preserve`：只替换默认路径解析，保留现有 registry 逻辑和显式注入 |
| M | `.agents/skills/hyperframes-curated-intake/scripts/build-registry-view.py` | 默认库消费者 | `manual-preserve`：沿用 `_registry.default_library()`，仅处理迁移所需冲突 |
| M | `.agents/skills/hyperframes-curated-intake/scripts/prepare-project.py` | 生产 CLI 调用方 | `manual-preserve`：不重写当前 v2 流程，只接入统一默认/传入库路径 |
| M | `.agents/skills/hyperframes-curated-intake/scripts/select-project-palette.py` | 生产 CLI 调用方 | `manual-preserve`：保留现有路由改动，只改库解析/帮助文本 |
| M | `.agents/skills/hyperframes-curated-intake/scripts/stage-selected-items.py` | staging 生产调用方 | `manual-preserve`：保留 source/hash/staging 行为，只改 canonical 源定位 |
| ?? | `.agents/skills/hyperframes-curated-intake/scripts/build-legacy-aliases.py` | 生成内容含旧根路径 | `unresolved`：未跟踪脚本的纳入与修改授权未被单独证实；B2 前需确认 |
| ?? | `.agents/skills/hyperframes-brief-controller/SKILL.md` | 直接引用根 frames / registry | `unresolved`：未跟踪 Skill 的纳入与跨 Skill 路径改写授权未被单独证实 |
| ?? | `.agents/skills/hyperframes-brief-controller/references/brief-contract.md` | 示例直接引用根库 | `unresolved`：未跟踪合同的纳入与改写授权未被单独证实 |
| M | `schemas/library.schema.json` | 迁移计划要求联动 Schema | `manual-preserve`：路径迁移不改已有 schema 语义；若确需结构变化则推迟到 C，不在 B 合并 |
| ?? | `tests/unit/test_library_routing_contract.py` | 真实库路径断言 | `unresolved`：未跟踪测试的纳入/改写授权未被单独证实；B2 前需确认 |
| ?? | `tests/unit/test_video_spec_handoff_refactor.py` | Frame 与 handoff 真实库路径 | `unresolved`：未跟踪且当前 4 个失败的测试；B 不借路径迁移改写验收语义 |
| M | `library/catalog.json` | B1 canonical 复制输入；B2 后旧根删除候选 | `unresolved`：可读取并冻结，但未证实可将未提交版本确认为新 canonical 或删除旧文件 |
| M | `library/director-catalog.json` | B1 派生投影复制输入 | `unresolved`：可做字节验证；重建、覆盖和旧根删除需授权 |
| M | `library/inventory-latest.json` | B1 清单锚点 | `unresolved`：只能作为冻结证据读取；覆盖或旧根删除需授权 |
| M | `library/provenance/curated-registry-build.json` | B1 provenance 复制输入 | `unresolved`：当前修改归属未确认；只能原样读取/比对 |
| M | `library/registry/registry.json` | B1 registry 投影复制输入 | `unresolved`：当前修改归属未确认；只能原样读取/比对 |
| M | `library/visual-director-block-candidates.json` | B1 candidate 清单复制输入 | `unresolved`：当前修改归属未确认；只能原样读取/比对 |
| ?? | `library/legacy-component-aliases.json` | B1 派生清单复制输入 | `unresolved`：未跟踪产物是否纳入 canonical 快照尚未授权 |
| ?? | `library/provenance/legacy-registry-verification.json` | B1 验证记录复制输入 | `unresolved`：未跟踪产物是否纳入 canonical 快照尚未授权 |
| ?? | `library/registry/blocks/before-after-wipe/` | B1 registry 投影输入 | `unresolved`：目录内未跟踪文件不得删除/覆盖；是否纳入新库快照待确认 |
| ?? | `library/registry/blocks/caption-camera-follow/` | B1 registry 投影输入 | `unresolved`：同上 |
| ?? | `library/registry/blocks/chatgpt-desktop-exchange/` | B1 registry 投影输入 | `unresolved`：同上 |
| ?? | `library/registry/blocks/code-snippet-apple-terminal-clear-dark/` | B1 registry 投影输入 | `unresolved`：同上 |
| ?? | `library/registry/blocks/code-snippet-dark-plus/` | B1 registry 投影输入 | `unresolved`：同上 |
| ?? | `library/registry/blocks/film-credits-stagger/` | B1 registry 投影输入 | `unresolved`：同上 |
| ?? | `library/registry/blocks/ordered-dither-pass/` | B1 registry 投影输入 | `unresolved`：同上 |
| ?? | `library/registry/blocks/particle-text-dissolve/` | B1 registry 投影输入 | `unresolved`：同上 |
| ?? | `library/registry/blocks/stitched-text-draw/` | B1 registry 投影输入 | `unresolved`：同上 |
| ?? | `library/registry/blocks/telemetry-hud/` | B1 registry 投影输入 | `unresolved`：同上 |
| ?? | `library/registry/blocks/testimonial-proof-card/` | B1 registry 投影输入 | `unresolved`：同上 |
| ?? | `library/registry/blocks/variable-axis-type/` | B1 registry 投影输入 | `unresolved`：同上 |
| ?? | `library/registry/blocks/wechat-desktop-exchange/` | B1 registry 投影输入 | `unresolved`：同上 |

上述 Git 状态按目录折叠的 `??` registry 内容展开如下。每个文件都是独立的 unresolved 输入，不因同目录共享策略而自动获得授权：

| 授权状态 | 具体文件 | 文件级策略 |
| --- | --- | --- |
| `unresolved` | `library/registry/blocks/before-after-wipe/assets/fonts/BarlowCondensed-ExtraBold.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/before-after-wipe/assets/fonts/Inter-400.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/before-after-wipe/assets/fonts/Inter-700.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/before-after-wipe/assets/fonts/JetBrainsMono-400.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/before-after-wipe/assets/fonts/JetBrainsMono-700.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/before-after-wipe/assets/vendor/gsap.min.js` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/before-after-wipe/before-after-wipe.html` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/before-after-wipe/registry-item.json` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/caption-camera-follow/assets/fonts/BarlowCondensed-ExtraBold.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/caption-camera-follow/assets/fonts/Inter-400.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/caption-camera-follow/assets/fonts/Inter-700.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/caption-camera-follow/assets/fonts/JetBrainsMono-400.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/caption-camera-follow/assets/fonts/JetBrainsMono-700.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/caption-camera-follow/assets/vendor/gsap.min.js` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/caption-camera-follow/caption-camera-follow.html` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/caption-camera-follow/registry-item.json` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/chatgpt-desktop-exchange/assets/vendor/gsap.min.js` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/chatgpt-desktop-exchange/chatgpt-desktop-exchange.html` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/chatgpt-desktop-exchange/registry-item.json` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/code-snippet-apple-terminal-clear-dark/assets/fonts/BarlowCondensed-ExtraBold.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/code-snippet-apple-terminal-clear-dark/assets/fonts/Inter-400.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/code-snippet-apple-terminal-clear-dark/assets/fonts/Inter-700.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/code-snippet-apple-terminal-clear-dark/assets/fonts/JetBrainsMono-400.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/code-snippet-apple-terminal-clear-dark/assets/fonts/JetBrainsMono-700.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/code-snippet-apple-terminal-clear-dark/assets/vendor/gsap.min.js` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/code-snippet-apple-terminal-clear-dark/code-snippet-apple-terminal-clear-dark.html` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/code-snippet-apple-terminal-clear-dark/registry-item.json` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/code-snippet-dark-plus/assets/fonts/BarlowCondensed-ExtraBold.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/code-snippet-dark-plus/assets/fonts/Inter-400.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/code-snippet-dark-plus/assets/fonts/Inter-700.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/code-snippet-dark-plus/assets/fonts/JetBrainsMono-400.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/code-snippet-dark-plus/assets/fonts/JetBrainsMono-700.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/code-snippet-dark-plus/assets/vendor/gsap.min.js` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/code-snippet-dark-plus/code-snippet-dark-plus.html` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/code-snippet-dark-plus/registry-item.json` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/film-credits-stagger/assets/vendor/gsap.min.js` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/film-credits-stagger/film-credits-stagger.html` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/film-credits-stagger/registry-item.json` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/ordered-dither-pass/assets/fonts/BarlowCondensed-ExtraBold.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/ordered-dither-pass/assets/fonts/Inter-400.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/ordered-dither-pass/assets/fonts/Inter-700.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/ordered-dither-pass/assets/fonts/JetBrainsMono-400.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/ordered-dither-pass/assets/fonts/JetBrainsMono-700.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/ordered-dither-pass/assets/vendor/gsap.min.js` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/ordered-dither-pass/ordered-dither-pass.html` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/ordered-dither-pass/registry-item.json` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/particle-text-dissolve/assets/fonts/BarlowCondensed-ExtraBold.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/particle-text-dissolve/assets/fonts/Inter-400.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/particle-text-dissolve/assets/fonts/Inter-700.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/particle-text-dissolve/assets/fonts/JetBrainsMono-400.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/particle-text-dissolve/assets/fonts/JetBrainsMono-700.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/particle-text-dissolve/assets/vendor/gsap.min.js` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/particle-text-dissolve/particle-text-dissolve.html` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/particle-text-dissolve/registry-item.json` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/stitched-text-draw/assets/fonts/BarlowCondensed-ExtraBold.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/stitched-text-draw/assets/fonts/Inter-400.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/stitched-text-draw/assets/fonts/Inter-700.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/stitched-text-draw/assets/fonts/JetBrainsMono-400.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/stitched-text-draw/assets/fonts/JetBrainsMono-700.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/stitched-text-draw/assets/vendor/gsap.min.js` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/stitched-text-draw/registry-item.json` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/stitched-text-draw/stitched-text-draw.html` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/telemetry-hud/assets/fonts/BarlowCondensed-ExtraBold.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/telemetry-hud/assets/fonts/Inter-400.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/telemetry-hud/assets/fonts/Inter-700.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/telemetry-hud/assets/fonts/JetBrainsMono-400.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/telemetry-hud/assets/fonts/JetBrainsMono-700.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/telemetry-hud/assets/vendor/gsap.min.js` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/telemetry-hud/registry-item.json` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/telemetry-hud/telemetry-hud.html` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/testimonial-proof-card/assets/fonts/BarlowCondensed-ExtraBold.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/testimonial-proof-card/assets/fonts/Inter-400.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/testimonial-proof-card/assets/fonts/Inter-700.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/testimonial-proof-card/assets/fonts/JetBrainsMono-400.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/testimonial-proof-card/assets/fonts/JetBrainsMono-700.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/testimonial-proof-card/assets/vendor/gsap.min.js` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/testimonial-proof-card/registry-item.json` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/testimonial-proof-card/testimonial-proof-card.html` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/variable-axis-type/assets/fonts/BarlowCondensed-ExtraBold.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/variable-axis-type/assets/fonts/Inter-400.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/variable-axis-type/assets/fonts/Inter-700.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/variable-axis-type/assets/fonts/JetBrainsMono-400.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/variable-axis-type/assets/fonts/JetBrainsMono-700.woff2` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/variable-axis-type/assets/vendor/gsap.min.js` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/variable-axis-type/registry-item.json` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/variable-axis-type/variable-axis-type.html` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/wechat-desktop-exchange/assets/vendor/gsap.min.js` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/wechat-desktop-exchange/registry-item.json` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |
| `unresolved` | `library/registry/blocks/wechat-desktop-exchange/wechat-desktop-exchange.html` | B1 只允许在用户确认后原样复制并逐字节验证；禁止覆盖、重建或删除源文件 |

## 5. 工作树归属矩阵

以下状态均在 Sprint A 开始前已存在，全部归属用户 / v2 工作。`M` 为已修改、`D` 为已删除、`??` 为未跟踪。Sprint A 对这些路径一律只读。

### 5.1 Curated Intake Skill

| 状态 | 路径 |
| --- | --- |
| M | `.agents/skills/hyperframes-curated-intake/SKILL.md` |
| M | `.agents/skills/hyperframes-curated-intake/agents/openai.yaml` |
| M | `.agents/skills/hyperframes-curated-intake/references/artifact-contract.md` |
| D | `.agents/skills/hyperframes-curated-intake/references/build-plan.schema.json` |
| D | `.agents/skills/hyperframes-curated-intake/references/creative-defaults.md` |
| M | `.agents/skills/hyperframes-curated-intake/references/curated-intake-request.schema.json` |
| M | `.agents/skills/hyperframes-curated-intake/references/curated-intake-result.schema.json` |
| M | `.agents/skills/hyperframes-curated-intake/references/curation.schema.json` |
| M | `.agents/skills/hyperframes-curated-intake/references/handoff.md` |
| M | `.agents/skills/hyperframes-curated-intake/references/intake-and-approval.md` |
| D | `.agents/skills/hyperframes-curated-intake/references/library.md` |
| D | `.agents/skills/hyperframes-curated-intake/references/scene-contract.schema.json` |
| D | `.agents/skills/hyperframes-curated-intake/references/scene-contracts.md` |
| M | `.agents/skills/hyperframes-curated-intake/references/storyboard-spec.schema.json` |
| D | `.agents/skills/hyperframes-curated-intake/references/teaching-visual-direction.md` |
| M | `.agents/skills/hyperframes-curated-intake/references/usage.schema.json` |
| M | `.agents/skills/hyperframes-curated-intake/references/verification.md` |
| ?? | `.agents/skills/hyperframes-curated-intake/references/library-routing.md` |
| ?? | `.agents/skills/hyperframes-curated-intake/references/motion-contract.md` |
| ?? | `.agents/skills/hyperframes-curated-intake/references/storyboard-authoring.md` |
| M | `.agents/skills/hyperframes-curated-intake/scripts/_curation.py` |
| M | `.agents/skills/hyperframes-curated-intake/scripts/_registry.py` |
| M | `.agents/skills/hyperframes-curated-intake/scripts/_routed.py` |
| M | `.agents/skills/hyperframes-curated-intake/scripts/allocate-beats.py` |
| M | `.agents/skills/hyperframes-curated-intake/scripts/build-registry-view.py` |
| M | `.agents/skills/hyperframes-curated-intake/scripts/prepare-project.py` |
| M | `.agents/skills/hyperframes-curated-intake/scripts/select-project-palette.py` |
| M | `.agents/skills/hyperframes-curated-intake/scripts/stage-selected-items.py` |
| M | `.agents/skills/hyperframes-curated-intake/scripts/verify-beats.py` |
| M | `.agents/skills/hyperframes-curated-intake/scripts/verify-curation.py` |
| M | `.agents/skills/hyperframes-curated-intake/scripts/verify-handoff.py` |
| ?? | `.agents/skills/hyperframes-curated-intake/scripts/_capabilities.py` |
| ?? | `.agents/skills/hyperframes-curated-intake/scripts/_routing.py` |
| ?? | `.agents/skills/hyperframes-curated-intake/scripts/apply-video-spec-refactor.py` |
| ?? | `.agents/skills/hyperframes-curated-intake/scripts/build-director-catalog.py` |
| ?? | `.agents/skills/hyperframes-curated-intake/scripts/build-legacy-aliases.py` |
| ?? | `.agents/skills/hyperframes-curated-intake/scripts/enrich-catalog-capabilities.py` |
| ?? | `.agents/skills/hyperframes-curated-intake/scripts/migrate-storyboard-v1-to-v2.py` |
| ?? | `.agents/skills/hyperframes-curated-intake/scripts/verify-legacy-registry.py` |
| ?? | `.agents/skills/hyperframes-curated-intake/scripts/verify-library-contract.py` |

### 5.2 根 library、Schema 与测试

| 状态 | 路径 |
| --- | --- |
| M | `library/catalog.json` |
| M | `library/director-catalog.json` |
| M | `library/inventory-latest.json` |
| M | `library/provenance/curated-registry-build.json` |
| M | `library/registry/registry.json` |
| M | `library/visual-director-block-candidates.json` |
| ?? | `library/legacy-component-aliases.json` |
| ?? | `library/provenance/legacy-registry-verification.json` |
| ?? | `library/registry/blocks/before-after-wipe/` |
| ?? | `library/registry/blocks/caption-camera-follow/` |
| ?? | `library/registry/blocks/chatgpt-desktop-exchange/` |
| ?? | `library/registry/blocks/code-snippet-apple-terminal-clear-dark/` |
| ?? | `library/registry/blocks/code-snippet-dark-plus/` |
| ?? | `library/registry/blocks/film-credits-stagger/` |
| ?? | `library/registry/blocks/ordered-dither-pass/` |
| ?? | `library/registry/blocks/particle-text-dissolve/` |
| ?? | `library/registry/blocks/stitched-text-draw/` |
| ?? | `library/registry/blocks/telemetry-hud/` |
| ?? | `library/registry/blocks/testimonial-proof-card/` |
| ?? | `library/registry/blocks/variable-axis-type/` |
| ?? | `library/registry/blocks/wechat-desktop-exchange/` |
| M | `schemas/library.schema.json` |
| M | `tests/unit/test_curated_intake_workflow.py` |
| M | `tests/unit/test_curated_routed_mode.py` |
| ?? | `tests/unit/test_library_routing_contract.py` |
| ?? | `tests/unit/test_video_spec_handoff_refactor.py` |

### 5.3 相邻 v2 / 视频工作

| 状态 | 路径 |
| --- | --- |
| ?? | `.agents/skills/hyperframes-brief-controller/` |
| D | `projects/curated-intake-v2-promo/assets/library/promo-runtime.js` |
| D | `projects/curated-intake-v2-promo/compositions/bind-the-motion.html` |
| D | `projects/curated-intake-v2-promo/compositions/frame-audition.html` |
| D | `projects/curated-intake-v2-promo/compositions/handoff-to-hyperframes.html` |
| D | `projects/curated-intake-v2-promo/compositions/idea-to-authority.html` |
| D | `projects/curated-intake-v2-promo/compositions/prove-the-handoff.html` |
| D | `projects/curated-intake-v2-promo/compositions/route-the-library.html` |
| D | `projects/curated-intake-v2-promo/compositions/select-the-source.html` |
| D | `projects/curated-intake-v2-promo/compositions/thesis-over-icon.html` |
| M | `projects/curated-intake-v2-promo/index.html` |
| D | `projects/curated-intake-v2-promo/package.json` |
| D | `projects/curated-intake-v2-promo/scripts/verify-motion-contract.cjs` |
| ?? | `HYPERFRAMES_VISUAL_DIRECTOR_SKILL_SPEC.md` |
| ?? | `video-spec-builder/` |
| ?? | `video-spec.md` |
| ?? | `videos/` |

### 5.4 仓库级未跟踪边界

| 状态 | 路径 | 说明 |
| --- | --- | --- |
| ?? | `AGENTS.md` | 当前仓库协作约束；不得覆盖 |
| ?? | `docs/curated-intake-lean-refactor-plan.md` | 本轮上游计划；不得修改 |

## 6. 阶段 B 门禁

结论：阶段 B 总体仍为 **BLOCKED**；B1（原样复制 + 字节/哈希验证）与 B2（preserve-and-layer 默认路径切换）分别获得 **CONDITIONAL GO** 并已完成；B3 及之后仍为 **BLOCKED**。

阻塞原因：根库包含尚未提交的修改和未跟踪 registry 产物，当前没有证据证明可以把这些内容固化为新的 canonical source、移动或删除；多个 B2 调用方本身也有未提交或未跟踪的 v2 工作，纳入和合并授权为 `unresolved`。此外，两条实际 pytest 命令均以 exit code 1 结束。inventory 的 0 errors 证明当前库内部可清点，不等同于迁移授权或完整回归通过。

### 6.1 转为 `CONDITIONAL GO` 的条件

用户确认记录：用户在 Sprint B1 指令中明确授权从当前根 `library/` 原样复制到新建 `.agents/skills/hyperframes-curated-intake/assets/library/`，并把所有权严格限制为新库目录和本基线文档；同时明确禁止删除、覆盖、重建、切换调用方或修改其他 dirty 工作。该确认只覆盖 B1，不构成 B2+ 的合并、切流或删除授权。

B1 执行前必须满足以下条件，才从 BLOCKED 转为 **CONDITIONAL GO**；本次执行已逐项满足：

1. 用户明确确认“当前 dirty 根 `library/` 工作树快照”可作为 B1 复制输入，包括第 4.2 节列出的 M / ?? 库文件和 registry 目录；未确认项继续保持 `unresolved`。
2. 再次冻结 `git status --short`、文件数、总字节数、duplicate 汇总、`inventory-latest.json` 和三项关键 SHA；若与本基线不同，先更新并重新审核基线，不自行选择新旧版本。
3. `.agents/skills/hyperframes-curated-intake/assets/library/` 仍为 missing 或经核对为空；任何既有目标内容都必须先确认归属，禁止覆盖。
4. B1 只做从根库到 Skill 内库的原样复制，不重建 catalog / registry，不修改调用方、Schema、文档或测试，不删除根库，也不修改 `source-provenance.json`。
5. 复制后以 `library/inventory-latest.json` 逐项核对 356 个 entry、全部 source file hash、162 个 registry mapping、8 个 Frame 和 errors / warnings；同时复算 1,576 个文件、52,862,307 bytes、重复项汇总和三项关键 SHA，结果必须与本基线完全一致。
6. 第 4.1 节三个 candidate source 及其 SHA 必须在 Skill 内库同相对路径逐字节保留；不能用相同 registry 投影替代或省略它们。
7. B1 结束时根 `library/` 仍保持原状且仍是 canonical；新副本只作为未切流的验证副本，并设置后续 B2 必须及时切流/清理的明确边界，避免被误认为已经完成双库迁移。

该 B1 条件放行本身**不适用于 B2 及之后**。B2 后来通过第 6.3 节记录的独立 preserve-and-layer 授权执行；B3+、旧根库删除以及任何库内容重建继续为 **BLOCKED**。既有 4 个 handoff 失败必须继续单独追踪，不能被库迁移掩盖或改写验收语义。

### 6.2 B1 实际结果

执行时间：`2026-09-04T22:28:46+08:00`。

预检确认目标 `.agents/skills/hyperframes-curated-intake/assets/library/` 不存在，因此没有覆盖冲突。随后使用单一 PowerShell shell 的 `Copy-Item -LiteralPath <root-library> -Destination <skill-assets> -Recurse` 做机械复制；未调用任何 catalog / registry / inventory 生成器，未修改调用方、Schema、tests、SKILL 或 references，未删除或改写根 `library/`。

复制后通过独立文件枚举校验，不依赖 inventory 的汇总结论：两端相对路径统一为 `/` 分隔后比较集合；对共同路径逐个比较文件大小和 SHA-256。

| 校验项 | 根 `library/` | Skill 内副本 | 差异 |
| --- | ---: | ---: | ---: |
| 文件数 | 1,576 | 1,576 | 0 |
| 总字节数 | 52,862,307 | 52,862,307 | 0 |
| 缺失相对路径 | — | — | 0 |
| 额外相对路径 | — | — | 0 |
| 文件大小不一致 | — | — | 0 |
| 文件 SHA-256 不一致 | — | — | 0 |

Skill 内副本关键文件 SHA-256：

| 文件 | SHA-256 | 与根库基线 |
| --- | --- | --- |
| `assets/library/catalog.json` | `5b022cd3ee07ee7efb90faf676cbb340daec65247a859fdd618561dd2064c8f2` | 一致 |
| `assets/library/registry/registry.json` | `e9e643262315e583948965f7275f10a0a984e8bcfe7303269505d1f0397ef1e2` | 一致 |
| `assets/library/inventory-latest.json` | `d147f8faca478fe4284397d2222df31b8329b3610cce765a51e64b5a015a7fea` | 一致 |

B1 结果：**PASS**。在 B1 完成时 Skill 内目录是已验证、尚未切流的副本，根 `library/` 仍保持 canonical；B1 本身没有解除 B2+ 门禁。随后 B2 由独立合同切换默认事实源，见下一节。

### 6.3 B2 preserve-and-layer 执行记录

用户确认记录：用户明确授权 Generator 实施 Sprint B2，要求保留并适配 dirty v2 改动，以 `_registry.default_library()` 作为唯一默认路径事实源，把生产调用与文档层叠切换到 `.agents/skills/hyperframes-curated-intake/assets/library`；同时禁止回退他人改动、修改库内容、运行库生成器、删除根库或扩展到 B3/C/D/E。该授权把 B2 从 BLOCKED 转为 **CONDITIONAL GO**，只覆盖本节列出的默认路径、调用文档、provenance target 和测试变更。

执行完成时间：`2026-09-04T23:24:14+08:00`。

B2 实际变更：

- `_registry.default_library()` 改为基于自身文件位置解析当前 Skill 的 `assets/library`，不依赖 cwd；10 个 Curated library CLI 共用该默认值并保留显式 `--library` 覆盖。
- `build-legacy-aliases.py` 的 `source` 改为实际解析后的输入 `catalog.json` 路径；默认 canonical 与显式外部库均由测试覆盖，未运行生成器写入任一真实库。
- Visual Director inventory 脚本保持 `--library` 必填，并把同一解析路径用于 talkcraft inventory 写入、Curated builder 透传和 director catalog 读取；脚本无需修改。
- README、CONTRIBUTING、Curated Intake / Brief Controller / Visual Director 三个 Skill、library routing 和 brief contract 的生产路径切到 Skill 内 canonical library；根 `library/` 仅标记为冻结兼容镜像。
- `source-provenance.json` 只改 3 条 active derived target 到 Skill 内 canonical candidate 路径；3 条 `hyperframes-ui-motion-library` source origin 保持原样。
- 四个真实库测试切到 Skill 内 canonical library；临时库测试继续使用显式覆盖。未创建 Skill 内 tests 目录。

#### 库 manifest 前后不变证据

manifest 算法与 B1 一致：规范化 `/` 相对路径，逐文件记录 size + SHA-256，按路径排序后对 UTF-8 manifest 文本再次计算 SHA-256。

| 时点 / 库 | files | bytes | manifest SHA-256 |
| --- | ---: | ---: | --- |
| B2 前：根 `library/` | 1,576 | 52,862,307 | `f19b4a1871c909b262dea0c2281ad43a13a98de3a76e76fec402730ff80e061f` |
| B2 前：Skill canonical library | 1,576 | 52,862,307 | `f19b4a1871c909b262dea0c2281ad43a13a98de3a76e76fec402730ff80e061f` |
| B2 后：根 `library/` | 1,576 | 52,862,307 | `f19b4a1871c909b262dea0c2281ad43a13a98de3a76e76fec402730ff80e061f` |
| B2 后：Skill canonical library | 1,576 | 52,862,307 | `f19b4a1871c909b262dea0c2281ad43a13a98de3a76e76fec402730ff80e061f` |

B2 后两库交叉比较：missing paths `0`、extra paths `0`、size mismatches `0`、SHA-256 mismatches `0`。因此 B2 没有删除、重建、同步或改写任何库文件。

#### 验证命令与结果

```powershell
python -c "import ast,pathlib; files=list(pathlib.Path('.agents/skills/hyperframes-curated-intake/scripts').glob('*.py'))+list(pathlib.Path('tests/unit').glob('test_*.py')); [ast.parse(p.read_text(encoding='utf-8'), filename=str(p)) for p in files]; print(f'parsed={len(files)}')"
python -m pytest tests/unit/test_library_routing_contract.py
python -m pytest tests/unit/test_library_routing_contract.py tests/unit/test_video_spec_handoff_refactor.py tests/unit/test_talkcraft_director_inventory.py tests/unit/test_visual_director_block_candidates.py
python -m pytest tests/unit
python -m pytest tests/unit --ignore=tests/unit/test_video_spec_handoff_refactor.py
```

| 验证 | exit code | 结果 |
| --- | ---: | --- |
| Python AST 解析 | 0 | 29 个脚本/测试文件解析成功 |
| library routing contract | 0 | 6 passed |
| 四个真实库测试文件 | 1 | 14 passed，4 failed，0 skipped，0 errors |
| 全 `tests/unit` | 1 | 33 passed，4 failed，0 skipped，0 errors |
| 排除已知 handoff 基线文件的 `tests/unit` | 0 | 33 passed |

两次 exit code 1 仍仅包含第 2 节已冻结的 4 个完整 node ID，没有新增失败：

1. `tests/unit/test_video_spec_handoff_refactor.py::VideoSpecHandoffRefactorTests::test_all_eight_inventory_frames_materialize_byte_exact`
2. `tests/unit/test_video_spec_handoff_refactor.py::VideoSpecHandoffRefactorTests::test_handoff_validates_media_and_writes_only_thin_compatibility_brief`
3. `tests/unit/test_video_spec_handoff_refactor.py::VideoSpecHandoffRefactorTests::test_template_is_upstream_only`
4. `tests/unit/test_video_spec_handoff_refactor.py::VideoSpecHandoffRefactorTests::test_unknown_media_reference_fails_closed`

B2 结果：**PASS within baseline**。canonical 默认路径、显式覆盖、legacy source、Visual Director 必填透传和不写根库均有测试或静态证据；B3/C/D/E 与根兼容镜像删除仍为 **BLOCKED**。

### 6.4 B3 clean-room 派生尝试（BLOCKED）

用户确认记录：用户明确授权 Sprint B3 的 clean-room 派生验证，并解决 B2/B3 legacy source 冲突：`legacy-component-aliases.json#source` 固定为 library-root-relative POSIX `catalog.json`，显式 `--library` 只控制读取位置，不进入产物。授权允许修改确定性派生集，但同时冻结根 `library/`、canonical source 集，并要求所有 clean-room JSON 禁止 `C:/Users/...` 绝对路径。

执行时间：`2026-09-04T23:47:07+08:00`。结论：**BLOCKED；NOT READY_FOR_B4**。

#### 已实施的合同修正

- `.agents/skills/hyperframes-curated-intake/scripts/build-legacy-aliases.py` 现在固定输出 `"source": "catalog.json"`。
- `tests/unit/test_library_routing_contract.py` 同时验证默认 canonical 输入和显式临时库覆盖都输出 `catalog.json`，并继续验证根库不被写入。
- 未同步任何 canonical 派生文件，未删除任何 canonical registry 文件，未执行 B4。

#### TalkCraft pinned 复现

对象库：`C:/Users/buend/Desktop/complex suite/video-talkcraft`。只读观察到当前 HEAD `082a896c120c3b0ce70f6fffc4d82c6cff4b4f9e`、79 cards 且工作树有既有修改；未 checkout、reset、stash、clean 或修改该仓库。

通过 `git archive --format=tar --output=<verified-temp-tar> 05691f5f25d91d211f793f5bb0d6941d3ef5723d` 导出到独立临时目录，并用只指向对象库的临时 Git metadata 固定 HEAD 与 origin。导出结果：

| 项目 | canonical | clean-room | 差异 |
| --- | --- | --- | ---: |
| cards | 78 | 78 | 0 |
| source commit | `05691f5f25d91d211f793f5bb0d6941d3ef5723d` | `05691f5f25d91d211f793f5bb0d6941d3ef5723d` | 0 |
| missing IDs / extra IDs | — | — | 0 / 0 |
| source/reference hash changes | — | — | 0 |
| `talkcraft-inventory.json` SHA-256 | `63248415a4d5619d057fbc380b781fa60254cf820f4e45d4c8bce9bed043beaf` | `63248415a4d5619d057fbc380b781fa60254cf820f4e45d4c8bce9bed043beaf` | byte-identical |

#### Clean-room 命令顺序与结果

两份独立 source-only 临时库均保留 catalog 声明的 362 个 source path，其中 59 个 source path 位于 `registry/`；只移除非 source 的 registry 投影及允许派生文件。首次把整个 `registry/` 误当派生的试运行正确地以 116/162 installable 失败，没有用于后续比较或同步。

每份有效 clean-room 都按以下顺序执行，所有步骤 exit code 0：

```powershell
python .agents/skills/hyperframes-visual-director/scripts/inventory-library.py --library <temp-library> --talkcraft <pinned-export>
python .agents/skills/hyperframes-curated-intake/scripts/build-registry-view.py --library <temp-library> --output <temp-library>/registry --report <temp-library>/provenance/curated-registry-build.json
python .agents/skills/hyperframes-curated-intake/scripts/build-legacy-aliases.py --library <temp-library> --output <temp-library>/legacy-component-aliases.json
python .agents/skills/hyperframes-curated-intake/scripts/build-director-catalog.py --library <temp-library> --check
python .agents/skills/hyperframes-curated-intake/scripts/verify-legacy-registry.py --library <temp-library> --output <temp-library>/provenance/legacy-registry-verification.json
python .agents/skills/hyperframes-curated-intake/scripts/verify-library-contract.py --library <temp-library>
python .agents/skills/hyperframes-curated-intake/scripts/inventory-library.py --library <temp-library> --output <temp-library>/inventory-latest.json
python .agents/skills/hyperframes-curated-intake/scripts/inventory-library.py --library <temp-library> --output <independent-temp-inventory.json>
```

- clean-room 派生文件：run 1 `924`、run 2 `924`；missing `0`、extra `0`、size/hash differences `0`。
- 每个 run 的两次 inventory 输出 byte-identical。
- canonical source freeze：canonical `710`、clean-room `710`；missing `0`、extra `0`、size/hash differences `0`。
- 相对 canonical 派生集：stale `1`（`registry/assets/fonts/OFL.txt`）；new `0`；changed `1`（`legacy-component-aliases.json`，仅 `source` 从 `library/catalog.json` 变为 `catalog.json`）。
- 由于下述 blocker，两项确定性差异均未 apply；stale 文件未删除。

#### 阻塞原因

全 JSON 扫描发现冻结 source `.agents/skills/hyperframes-curated-intake/assets/library/visual-director-block-candidates.json` 含 3 条 `C:/Users/buend/Desktop/mav-works/...` 绝对 source origin；两份 clean-room 因而各有 1 个违规 JSON（合计 6 个违规字段实例）。B3 合同同时规定该 source 文件不可修改、且所有 JSON 禁止 `C:/Users/...`，两项要求无法同时满足。

具体字段位于该文件的 3 个 `canonicalSource.path`：WeChat Desktop Exchange、ChatGPT Desktop Exchange、Film Credits Stagger。它们不是本轮生成的临时路径，也不是 TalkCraft 漂移；但在“所有 JSON”门禁下仍然违规。未获得修改冻结 provenance source 的授权，因此 Generator 不自行选择改写或豁免。

解除阻塞需要 Planner / 用户二选一修订合同：

1. 授权把这 3 条绝对 origin 迁移为稳定、可解析的非用户绝对引用，并联动 provenance 合同；或
2. 明确全 JSON 门禁只作用于本轮生成的派生 JSON，并为冻结 source 中已知的 3 条 origin 建立精确豁免。

在修订前不得同步 `legacy-component-aliases.json`、不得删除 `registry/assets/fonts/OFL.txt`、不得执行 canonical apply 后检查、staging 回归或 B4 删除。

#### 库保护与测试

| 时点 / 库 | files | bytes | manifest SHA-256 |
| --- | ---: | ---: | --- |
| B3 前：根 `library/` | 1,576 | 52,862,307 | `f19b4a1871c909b262dea0c2281ad43a13a98de3a76e76fec402730ff80e061f` |
| B3 后：根 `library/` | 1,576 | 52,862,307 | `f19b4a1871c909b262dea0c2281ad43a13a98de3a76e76fec402730ff80e061f` |
| B3 前：canonical library | 1,576 | 52,862,307 | `f19b4a1871c909b262dea0c2281ad43a13a98de3a76e76fec402730ff80e061f` |
| B3 后：canonical library | 1,576 | 52,862,307 | `f19b4a1871c909b262dea0c2281ad43a13a98de3a76e76fec402730ff80e061f` |

```powershell
python -m pytest tests/unit/test_library_routing_contract.py
python -m pytest tests/unit
git diff --check -- .agents/skills/hyperframes-curated-intake/scripts/build-legacy-aliases.py tests/unit/test_library_routing_contract.py docs/curated-intake-lean-refactor-baseline.md
```

- related tests：exit 0，6 passed。
- full unit：exit 1，33 passed / 4 failed；失败仍仅为第 2 节的 4 个既有 handoff node ID，新增失败 `0`。
- `git diff --check`：exit 0。

### 6.5 B3 修订合同前置阻塞（2026-09-05）

用户额外授权仅允许把 canonical `assets/library/visual-director-block-candidates.json` 中 3 条 `canonicalSource.path` 的旧前缀 `C:/Users/buend/Desktop/mav-works/mav-content-fac/` 精确移除，并要求替换后的仓库相对目标文件存在且实算 SHA-256 与各 entry 记录匹配。

修改前冻结结果：candidate manifest SHA-256 为 `f020b50aeb927707cf912f5685583d9bcdafc63777d1172700d612f008a7920d`；director catalog SHA-256 为 `bd753c173c8fe8778cb570ffdfff4e29ddab96068705bc4bdeecc1661380c735`。旧前缀恰好出现 3 次。

前置目标检查失败：当前仓库不存在 `.agents/skills/hyperframes-ui-motion-library/`，因此以下 3 个授权替换目标全部 missing：

| ID | 预期相对目标 | 记录的 SHA-256 | 结果 |
| --- | --- | --- | --- |
| `registry-block:wechat-desktop-exchange` | `.agents/skills/hyperframes-ui-motion-library/assets/library/compositions/wechat-desktop-exchange.html` | `e7678d16a5ea807ad51c062718b73840128dd9030b341be21541ebdfd43a792f` | missing |
| `registry-block:chatgpt-desktop-exchange` | `.agents/skills/hyperframes-ui-motion-library/assets/library/compositions/chatgpt-desktop-exchange.html` | `44ebeee49717e4c3a974e6c2f8a6e7308d4ac5038f65b9ed5a33f5345d9199e1` | missing |
| `registry-block:film-credits-stagger` | `.agents/skills/hyperframes-ui-motion-library/assets/library/compositions/film-credits-stagger.html` | `8662a6680adf4c73425298df366579c4f8f7857f836e14b4e35d569bf1d7bb3c` | missing |

对当前 workspace 的 `.agents/` 与根 `library/` HTML 做 SHA-256 扫描，也没有找到与上述 3 个 expected hash 匹配的文件。现有同名 candidate / registry 文件是 derived target，hash 分别为 `2e3e19...`、`423b15...`、`f75373...`，不能冒充 canonical source origin。

结论：修订 B3 仍为 **BLOCKED；NOT READY_FOR_B4**。本次前置检查未修改 candidate manifest、未创建新 clean-room、未同步或删除派生产物、未触碰根库。解除阻塞需要明确授权把缺失的 `hyperframes-ui-motion-library` 源文件纳入当前仓库，或再次修订 3 条 path 的可解析目标与对应 provenance 合同。

### 6.6 B3 修订合同解除阻塞与最终结果

用户 / Planner 随后澄清：3 条 `canonicalSource.path` 是相对于冻结的 `docs/library-provenance/source-provenance.json#hyperframesReferenceRepository.path` 的 POSIX 路径，不是相对于当前 `mav 3` 仓库。该澄清解除 6.5 的解析歧义；6.4–6.5 保留为未 apply 试运行的审计轨迹。最终执行完成时间：`2026-09-05T00:16:47+08:00`。

#### 外部 source 复验与精确规范化

只读复验外部参考仓库 `C:/Users/buend/Desktop/mav-works/mav-content-fac`：HEAD 为 `b752ef5d13db88b90cd0652db953cacdacea692a`，与 provenance 固定 commit 一致。未把该仓库的 Skill 或 HTML 复制到当前仓库。3 个相对目标均存在，实算 SHA-256 与 candidate entry 完全一致：

| ID | 相对 `hyperframesReferenceRepository.path` 的路径 | SHA-256 |
| --- | --- | --- |
| `registry-block:wechat-desktop-exchange` | `.agents/skills/hyperframes-ui-motion-library/assets/library/compositions/wechat-desktop-exchange.html` | `e7678d16a5ea807ad51c062718b73840128dd9030b341be21541ebdfd43a792f` |
| `registry-block:chatgpt-desktop-exchange` | `.agents/skills/hyperframes-ui-motion-library/assets/library/compositions/chatgpt-desktop-exchange.html` | `44ebeee49717e4c3a974e6c2f8a6e7308d4ac5038f65b9ed5a33f5345d9199e1` |
| `registry-block:film-credits-stagger` | `.agents/skills/hyperframes-ui-motion-library/assets/library/compositions/film-credits-stagger.html` | `8662a6680adf4c73425298df366579c4f8f7857f836e14b4e35d569bf1d7bb3c` |

canonical `visual-director-block-candidates.json` 仅移除这 3 个 path 的旧绝对前缀：旧前缀出现数从 `3` 变为 `0`，新相对前缀恰好 `3`；文本 diff 仅 3 行，遮蔽这 3 个字段后的结构化 JSON 完全相等，ID/hash/其他字段/格式均未改变。文件 SHA-256 从 `f020b50aeb927707cf912f5685583d9bcdafc63777d1172700d612f008a7920d` 变为 `9226b83d5f8c7541061bfc99cf559a91176209b2cb61d1eed99cec0a8f6440d8`。`build-director-catalog` 不读取此 manifest；规范化前后 director output SHA-256 均为 `bd753c173c8fe8778cb570ffdfff4e29ddab96068705bc4bdeecc1661380c735`。

#### 全新 clean-room、TalkCraft 与确定性

本次只使用全新目录 `C:/Users/buend/AppData/Local/Temp/curated-b3r-5a3e273337894ebb8153700c3cd50b60`，不依赖也不覆盖 6.4 的旧目录。两份 clean-room 都从规范化后的 canonical source-only 输入开始；每份保留 `710` 个 source 文件和 catalog 声明的 `362` 个 source path（包括位于 `registry/` 下的 `59` 个源文件），然后严格按 6.4 所列八条命令顺序重新生成。

TalkCraft 仍通过对象库的 Git object 在独立目录导出 commit `05691f5f25d91d211f793f5bb0d6941d3ef5723d`；结果 `78` cards，card ID missing/extra `0/0`，source/reference hash differences `0`，生成的 inventory 与 canonical byte-identical，SHA-256 `63248415a4d5619d057fbc380b781fa60254cf820f4e45d4c8bce9bed043beaf`。对象库当前 HEAD 在执行后仍为 `082a896c120c3b0ce70f6fffc4d82c6cff4b4f9e`，既有 `M workbench/src/cards/tpl-index.ts` 保持不变；未 checkout/reset/stash/clean。

两次 clean-room 的每一步 exit code 均为 `0`：每次派生集 `924` 个文件，两次之间 missing/extra/size-or-SHA differences 为 `0/0/0`；每次最后的两份独立 inventory byte-identical。两次 clean-room 的全部 JSON 中临时目录、用户绝对路径、根 `library` runtime 路径违规均为 `0`。

相对 apply 前 canonical 的确定性派生 delta 为：changed `1`、stale `1`、new `0`。

| 处置 | 路径 | 证据 |
| --- | --- | --- |
| 同步 changed | `legacy-component-aliases.json` | `source` 固定为 `catalog.json`；SHA-256 `a54234d1...` → `e5479f72419b470d1c29f9fc74f878bb98ffcc99ce7eeffc59df43b67e3a6196` |
| 删除 stale | `registry/assets/fonts/OFL.txt` | 两次 source-aware clean-room 都未生成，且不属于 710 个冻结 source 文件 |

没有同步其他文件。apply 后 canonical 与 clean-room run 1 做完整 `1,575` 文件的规范化 path/size/SHA 比较，missing `0`、extra `0`、differences `0`。

#### 保护门禁与 post-apply 验证

| 库 / 时点 | files | bytes | manifest SHA-256 |
| --- | ---: | ---: | --- |
| B3 前根 `library/` | 1,576 | 52,862,307 | `f19b4a1871c909b262dea0c2281ad43a13a98de3a76e76fec402730ff80e061f` |
| B3 后根 `library/` | 1,576 | 52,862,307 | `f19b4a1871c909b262dea0c2281ad43a13a98de3a76e76fec402730ff80e061f` |
| B3 后 canonical | 1,575 | 52,857,763 | `33c40b5947754baec276bbc7e0994d0d8eede72b285d3127f230fd4164dcefc1` |

根库完整 manifest 前后相同；canonical 的变化仅为已授权的 3 路径 source 规范化与上述 2 项派生 delta。规范化后的 canonical source 集与 clean-room source 集都是 `710` 文件，missing/extra/size-or-SHA differences 为 `0/0/0`。冻结的 `source-provenance.json` 未改；其外部仓库 locator 是 active provenance 的明确绝对路径例外。active canonical library 的 JSON 扫描中用户绝对路径、临时路径、根库 runtime 路径均为 `0`；冻结根兼容镜像中原有的 3 条旧绝对 candidate path 未改，留待 B4 整体删除而不做反向同步。

canonical apply 后只读/check 命令均 exit `0`：

```powershell
python .agents/skills/hyperframes-curated-intake/scripts/build-director-catalog.py --library .agents/skills/hyperframes-curated-intake/assets/library --check
python .agents/skills/hyperframes-curated-intake/scripts/verify-legacy-registry.py --library .agents/skills/hyperframes-curated-intake/assets/library --output <temp>/legacy-registry-verification.json
python .agents/skills/hyperframes-curated-intake/scripts/verify-library-contract.py --library .agents/skills/hyperframes-curated-intake/assets/library
python .agents/skills/hyperframes-curated-intake/scripts/inventory-library.py --library .agents/skills/hyperframes-curated-intake/assets/library --output <temp>/inventory-latest.json
```

临时 legacy verification 与 canonical provenance byte-identical；临时 inventory 与 canonical `inventory-latest.json` byte-identical。真实 staging 回归由 `test_default_and_explicit_staging_frame_and_director_selection_use_canonical_library` 覆盖：默认 canonical 与显式 canonical override 对 `registry-component:flow-complex` 生成相同 receipt，component 及 `frame:cobalt-grid` 的 staged 文件 SHA 与源文件一致；`talkcraft:alt-block-lines` 可由 director selection 从 pinned inventory 读出并 lint，但其 candidate 合同不可安装，因此未伪造 TalkCraft staging。测试同时证明不回退或写入根库。

#### 测试结果

```powershell
python -m pytest tests/unit/test_library_routing_contract.py tests/unit/test_visual_director_block_candidates.py
python -m pytest tests/unit
python -m pytest tests/unit --ignore=tests/unit/test_video_spec_handoff_refactor.py
git diff --check
```

| 命令 | exit code | 结果 |
| --- | ---: | --- |
| 两个 B3 focused files | 0 | 12 passed |
| 全 `tests/unit` | 1 | 35 passed / 4 failed / 0 skipped / 0 errors |
| 排除已知 handoff 基线 | 0 | 35 passed |
| `git diff --check` | 0 | 无 whitespace error |

全 unit 的 4 个失败仍严格等于第 2 节列出的 4 个 `test_video_spec_handoff_refactor.py` 完整 node ID；B3 新增失败为 `0`。

B3 最终结论：**PASS within frozen baseline；READY_FOR_B4**。该结论仅表示 B4 的前置迁移/确定性门禁已满足；本 Sprint 没有执行根库删除，也没有实施 C/D/E/F。

收尾时已先把新临时目录解析并验证为 `C:/Users/buend/AppData/Local/Temp` 的直接子目录，再尝试 `Remove-Item -LiteralPath <verified-temp> -Recurse -Force`；主机策略在进程创建前拒绝该命令，因此目录仍残留。未绕过策略，残留不影响上述已完成验收；6.4 的旧临时目录同样未触碰。

### 6.7 B4 根镜像退役记录

用户明确授权删除整个 `C:/Users/buend/Desktop/mav 3/library`。本节是删除后的当前状态；本文此前关于根库存在、dirty 状态、hash 和调用方的文字均是 Sprint A–B3 的历史审计记录，不再表示活动位置。执行完成时间：`2026-09-05T00:38:00+08:00`。

#### 删除前状态与可恢复归档

删除前再次以 hidden-aware 文件枚举复算根镜像：`1,576` files、`52,862,307` bytes、manifest SHA-256 `f19b4a1871c909b262dea0c2281ad43a13a98de3a76e76fec402730ff80e061f`。Git 分类为 tracked `1,485`、普通 untracked `91`、ignored `0`；因此归档覆盖 tracked dirty、untracked 与隐藏文件，没有 ignored 遗漏。

恢复归档保存在 workspace 外，至少保留到 Evaluator PASS：

| 项目 | 值 |
| --- | --- |
| 归档 | `C:/Users/buend/AppData/Local/Temp/curated-b4-archive-d39de3ae7e784e4987ac2366e5c5f978/root-library-recovery.tar` |
| 归档 bytes | `54,479,360` |
| 归档 SHA-256 | `9f7e34ea6401bcd858bc34b5f7fcb5846a2cf4b289196b5858434bcdaaef96ab` |
| tar 可列出 entries | `2,205`（文件和目录） |
| 清单文件 | 同目录 `root-library-manifest.tsv`，SHA-256 `f19b4a1871c909b262dea0c2281ad43a13a98de3a76e76fec402730ff80e061f` |

归档不是只做可列出检查：已实际解包到同一归档目录的 `restore-verification/library`，再按 path/size/SHA 复算，得到 `1,576 / 52,862,307 / f19b4a...061f`，与源完全一致。恢复方法已被实际验证为 `tar.exe -xf root-library-recovery.tar -C <empty-restore-directory>`；不得在 Evaluator PASS 前清理该归档目录。

#### 删除门禁与精确结果

删除前将 repo、target 与 parent 全部解析为绝对路径，确认 target 为 repo 的直接子目录、target 不等于 repo/home 且不含 glob。随后实际运行：

```powershell
git clean -nd -- library
git clean -ndx -- library
git rm -r -f -- library
git clean -fd -- library
```

两个 dry-run 的每个条目都位于精确授权目标；`-nd` 与 `-ndx` 输出相同，证明 ignored `0`，因此未执行 `git clean -fdx`。删除结果：tracked deletions `1,485`，清理普通 untracked `91`，总删除文件 `1,576`。`C:/Users/buend/Desktop/mav 3/library` 不存在；`git ls-files --others --exclude-standard -- library` 和 ignored 查询都为 `0`，`git status --short -- library` 只剩 `1,485` 条 tracked deletion。

#### Canonical 保护、调用方和回归

| 时点 | files | bytes | manifest SHA-256 |
| --- | ---: | ---: | --- |
| B4 前 canonical | 1,575 | 52,857,763 | `33c40b5947754baec276bbc7e0994d0d8eede72b285d3127f230fd4164dcefc1` |
| B4 后 canonical | 1,575 | 52,857,763 | `33c40b5947754baec276bbc7e0994d0d8eede72b285d3127f230fd4164dcefc1` |

B4 未运行任何写 canonical 的生成器。README、CONTRIBUTING、Curated Intake / Brief Controller / Visual Director 三个 Skill 已改为“根镜像已移除、不得重建或 fallback”；直接相关 references 已使用 canonical 路径，无需额外改写。`test_library_routing_contract.py` 的旧 byte-guard 已改为断言根路径始终不存在，同时继续断言 cwd-independent default 等于 Skill canonical、显式 override 有效。

最终 `rg --hidden` 扫描在排除明确的历史 plan/baseline、根不存在 guard、临时 fixture 以及项目 staging 的 `compositions/library` / `assets/library` 后，活动根库调用命中 `0`。历史 plan/baseline 中保留 `22` 个根库审计引用；测试中保留 `7` 个 `ROOT_LIBRARY` 不存在 guard；`tests/test_curated_registry_view.py` 的 `root / "library"` 是 `TemporaryDirectory` 内的显式外部库 fixture，不是仓库根调用方。

canonical post-delete 验证：

```powershell
python .agents/skills/hyperframes-curated-intake/scripts/build-director-catalog.py --library .agents/skills/hyperframes-curated-intake/assets/library --check
python .agents/skills/hyperframes-curated-intake/scripts/verify-legacy-registry.py --library .agents/skills/hyperframes-curated-intake/assets/library --output <temp>/legacy-registry-verification.json
python .agents/skills/hyperframes-curated-intake/scripts/verify-library-contract.py --library .agents/skills/hyperframes-curated-intake/assets/library
python .agents/skills/hyperframes-curated-intake/scripts/inventory-library.py --library .agents/skills/hyperframes-curated-intake/assets/library --output <temp>/inventory-latest.json
python .agents/skills/hyperframes-curated-intake/scripts/stage-selected-items.py --project <temp-copy-of-projects/curated-intake-v2-promo> --all-required
```

以上均 exit `0`；临时 legacy report 与 canonical byte-identical，临时 inventory 与 canonical byte-identical。真实项目源只读，staging 仅发生在独立临时副本。Evaluator 发现初版审计的 receipt items 数字错误；本次只读复核唯一 receipt `C:/Users/buend/AppData/Local/Temp/curated-b4-check-018fbb5f84934d3592cd02d5496d38da/curated-intake-v2-promo/.hyperframes/staging-receipt.json` 后更正为 `30`：lottie `8`、registry-block `7`、registry-component `12`、svg `3`。对应 curation 的 `selectedIds` 为 `30` 且 unique `30`，`missingIds` 为 `0`，stage count `= len(receipt.items) = 30`。这是 FAIL→fix 的证据更正；没有新增 ID、重跑 selection/staging 或修改 receipt。源项目既有 M/D 状态未改变。默认/显式 override、component/frame SHA 与 TalkCraft director selection 继续由 focused test 覆盖。

```powershell
python -m pytest tests/unit/test_library_routing_contract.py tests/unit/test_talkcraft_director_inventory.py tests/unit/test_visual_director_block_candidates.py
python -m pytest tests/unit
python -m pytest tests/unit --ignore=tests/unit/test_video_spec_handoff_refactor.py
git diff --check
```

| 验证 | exit code | 结果 |
| --- | ---: | --- |
| B4 focused unit | 0 | 16 passed |
| 全 `tests/unit` | 1 | 35 passed / 4 failed / 0 skipped / 0 errors |
| 排除已知 handoff 文件 | 0 | 35 passed |
| `git diff --check` | 0 | 无 whitespace error |

全 unit 的 4 个失败仍严格等于第 2 节的 4 个完整 node ID，B4 新增失败 `0`。一次额外的 `tests/test_curated_registry_view.py` 联跑完成了 Registry HTTP catalog/install 断言，但 Windows 在 `TemporaryDirectory` 收尾时因外部进程短暂占用 project 目录报 `PermissionError`；该非 unit 清理失败不涉及根库解析，也没有修改真实项目或 canonical。

B4 实现结论：**root absent；canonical preserved；active root references 0；ready_for Evaluator**。阶段 C 未开始。

### 6.8 C1 types：revision 14 最小导演合同

用户确认 C 阶段的过渡态：现有 `routing` 是六项导演 metadata 的唯一容器；旧 routing 字段只在 C 阶段暂存供 D 前兼容，不再扩张，阶段 D 负责迁移或删除。C1 只定义类型合同，不修改 canonical catalog、revision、library 文件、生成器、路由行为或派生产物；C2 尚未开始。

唯一 Schema 仍为根 `schemas/library.schema.json`，没有创建 Skill 内副本。实现采用根级 Draft 2020-12 `if revision == 14` / `then entries.items` 条件，再以 entry `kind` 条件只对 `registry-block`、`registry-component`、`svg`、`lottie` 要求 `routing` 的六项字段：

- `family`：`data/process/structure/compare/interface/concept/emphasis/evidence` 八枚举；
- `purpose`：非空、非纯空白、拒绝常见 placeholder；
- `useWhen`、`avoidWhen`、`expects`：非空数组、元素唯一，每项非空且非 placeholder；
- `motion`：`entrance-only/progressive/stateful` 三枚举；
- `fallbackIds`：继续可选；若存在必须是唯一的 catalog ID 形状数组。

基础 `routing` 仍声明旧字段并保持 `additionalProperties: false`，因此 revision 14 目标项可在迁移期间携带旧字段，但不能新增第二个 directing 容器。entry 与 catalog 的既有全局 required 和 `additionalProperties: false` 均未放松。revision 13 不触发新条件，当前 356-entry canonical catalog 继续整体验证通过。

冻结迁移 cohort 经测试确认：目标项 `232`（registry-block `48`、registry-component `123`、svg `31`、lottie `30`）；轻量 identity assets `111`（logo `95`、font `8`、sfx `3`、background `4`、texture `1`）不要求六项重复 metadata；out-of-C-scope `13`（motion-rule `4`、scene-blueprint `4`、transition `5`）合同原样且不要求六项。

`references/library-routing.md` 只补充 revision 14 类型边界、revision 13 迁移输入和 D 阶段兼容责任，并明确没有声称 canonical 已迁移。测试文件 `tests/unit/test_library_schema_revision14.py` 覆盖以下 node IDs：

1. `test_revision_13_canonical_catalog_remains_valid_and_has_the_frozen_migration_cohorts`
2. `test_revision_14_target_kinds_accept_the_six_field_contract_and_legacy_routing_fields`
3. `test_revision_14_target_kinds_reject_each_missing_directing_field`
4. `test_revision_14_rejects_unknown_family_and_motion_values`
5. `test_revision_14_rejects_empty_directing_arrays`
6. `test_revision_14_rejects_duplicate_directing_array_items`
7. `test_revision_14_rejects_empty_whitespace_and_placeholder_text`
8. `test_revision_14_light_identity_assets_pass_without_directing_metadata`
9. `test_revision_14_out_of_scope_contracts_pass_unchanged`
10. `test_revision_14_rejects_unknown_top_level_and_parallel_directing_metadata`
11. `test_revision_14_optional_fallback_ids_require_unique_catalog_id_shapes`

验证结果：

```powershell
python -m pytest tests/unit/test_library_schema_revision14.py
python -m pytest tests/unit/test_library_schema_revision14.py tests/unit/test_library_routing_contract.py tests/unit/test_talkcraft_director_inventory.py tests/unit/test_visual_director_block_candidates.py
python -m pytest tests/unit
python -m pytest tests/unit --ignore=tests/unit/test_video_spec_handoff_refactor.py
git diff --check
```

| 验证 | exit code | 结果 |
| --- | ---: | --- |
| C1 Schema focused | 0 | 33 passed |
| Schema + 相关 library unit | 0 | 49 passed |
| 全 `tests/unit` | 1 | 68 passed / 4 failed / 0 skipped / 0 errors |
| 排除已知 handoff 文件 | 0 | 68 passed |
| `git diff --check` | 0 | 无 whitespace error |

全 unit 的 4 个失败仍严格等于第 2 节记录的 4 个 `test_video_spec_handoff_refactor.py` node ID，C1 新增失败 `0`。保护复算：canonical 仍为 `1,575 files / 52,857,763 bytes / 33c40b5947754baec276bbc7e0994d0d8eede72b285d3127f230fd4164dcefc1`；`catalog.json` 仍为 revision `13`、SHA-256 `5b022cd3ee07ee7efb90faf676cbb340daec65247a859fdd618561dd2064c8f2`；根 `library/` 仍不存在，B4 的 `1,485` tracked deletions 保持不变。

C1 结论：**types contract complete；Evaluator PASS；C2 已在下节实施**。

### 6.9 C2 service：六项保留、事实投影与 revision 14 验证

审计说明：本节记录 C2 初次实现；其中曾保留的无参数 catalog apply 分支未通过 Evaluator 写边界验收，已由 6.10 的修订完整删除。当前行为以 6.10 为准。

C2 只使迁移与派生工具理解 C1 定义的合同，不策展 catalog、不提升 revision、不运行写 canonical 的生成器，也不进入 C3/D。六项 `routing.family/purpose/useWhen/avoidWhen/expects/motion` 继续是唯一导演选择权威；`framePolicy` 独立，旧 routing 字段继续只作 D 前兼容。

实现行为：

- `apply-video-spec-refactor.py` 在旧兼容字段迁移前深拷贝已有六项并逐值恢复；缺失的六项不会由 slug 或旧字段补造。新增 `--report`/`--check` 只生成非权威 proposal/conflict 报告，不写 catalog。`expects` 建议只来自 `requiredInputs`，`motion` 建议只来自 `motionHooks/supports`，并携带置信度；`purpose/useWhen/avoidWhen/family` 保持人工项，旧 family 与八枚举冲突只报告，绝不把 slug 当 family。
- `enrich-catalog-capabilities.py` 仍只更新 capability 事实，并以六项前后深比较防止越界写入。
- `build-director-catalog.py` 只从 catalog routing 逐值投影六项和可选 `fallbackIds`；TalkCraft 非 revision 14 catalog cohort，不伪造六项。
- `build-registry-view.py` 将相同投影放入 registry-item metadata 的 `routing`，同时保留 block 的旧 `dimensions`/`durationInFrames` 兼容字段，不改变 install 文件或哈希。
- `verify-library-contract.py` 仅在 revision `14` 启用严格检查：四类精确总量 `48/123/31/30 = 232`、六项完整性、枚举、非空/唯一/非 placeholder，以及 fallback 存在、ready、目标 cohort 和同 family。revision `13` 报告明确 `enforced: false`，当前 canonical 不误报。
- Curated Intake 与 Visual Director 的直接 routing/selection 引用文档同步说明上述选择权威、`framePolicy` 边界、C2 tooling-ready 与 canonical 仍是 revision 13 的事实。

非写入迁移报告命令对当前 canonical 返回预期 exit `1`（尚未策展），临时报告 `authoritative: false`：`targetEntries=232`、`readyEntries=0`、`needsManual=232`、`conflicts=158`。该报告位于 workspace 外临时路径，未签入 proposal、overlay 或 mapping；catalog 字节未改变。

新增 `tests/unit/test_library_tooling_revision14.py` 的完整 node IDs：

1. `test_apply_refactor_preserves_curated_directing_values_and_is_idempotent`
2. `test_apply_refactor_reports_legacy_family_conflicts_without_slug_inference`
3. `test_capability_enricher_never_changes_directing_metadata`
4. `test_director_projection_copies_catalog_directing_only_and_does_not_fabricate_talkcraft`
5. `test_registry_projection_preserves_directing_and_legacy_geometry_without_install_drift`
6. `test_revision14_verifier_accepts_complete_cohort`
7. `test_revision14_verifier_reports_missing_enum_placeholder_and_array_errors[purpose-None-fields missing]`
8. `test_revision14_verifier_reports_missing_enum_placeholder_and_array_errors[purpose-placeholder-invalid purpose]`
9. `test_revision14_verifier_reports_missing_enum_placeholder_and_array_errors[family-flow-invalid family]`
10. `test_revision14_verifier_reports_missing_enum_placeholder_and_array_errors[motion-loop-invalid motion]`
11. `test_revision14_verifier_reports_missing_enum_placeholder_and_array_errors[useWhen-value4-invalid useWhen]`
12. `test_revision14_verifier_reports_missing_enum_placeholder_and_array_errors[avoidWhen-value5-invalid avoidWhen]`
13. `test_revision14_verifier_reports_missing_enum_placeholder_and_array_errors[expects-value6-invalid expects]`
14. `test_revision14_verifier_checks_fallback_exists_ready_and_same_family`
15. `test_legacy_router_output_is_unchanged_by_idempotent_catalog_enrichment`
16. `test_no_revision14_proposal_or_overlay_is_committed`

验证命令与结果：

```powershell
python -m pytest tests/unit/test_library_tooling_revision14.py
python -m pytest tests/unit/test_library_tooling_revision14.py tests/unit/test_library_schema_revision14.py tests/unit/test_library_routing_contract.py tests/unit/test_talkcraft_director_inventory.py tests/unit/test_visual_director_block_candidates.py
python .agents/skills/hyperframes-curated-intake/scripts/build-director-catalog.py --check
python .agents/skills/hyperframes-curated-intake/scripts/verify-library-contract.py
python -m pytest tests/unit
python -m pytest tests/unit --ignore=tests/unit/test_video_spec_handoff_refactor.py
git diff --check
```

| 验证 | exit code | 结果 |
| --- | ---: | --- |
| C2 focused tooling | 0 | 16 passed |
| C1/C2 + 相关 library unit | 0 | 65 passed |
| Director catalog check | 0 | checked-in projection 与当前 catalog 一致 |
| 当前 revision 13 library contract | 0 | 162/162 Registry ready；revision 14 `enforced=false`；0 errors |
| 全 `tests/unit` | 1 | 84 passed / 4 failed / 0 skipped / 0 errors |
| 排除已知 handoff 文件 | 0 | 84 passed |
| `git diff --check` | 0 | 无 whitespace error |

全 unit 的 4 个失败仍严格等于第 2 节记录的 4 个 `test_video_spec_handoff_refactor.py` node ID，C2 新增失败 `0`；`_routing.py` 与选择脚本未修改，legacy router 输出前后逐值不变。最终以相同的规范化相对路径/size/SHA-256 manifest 算法独立复算：canonical 仍为 `1,575 files / 52,857,763 bytes / 33c40b5947754baec276bbc7e0994d0d8eede72b285d3127f230fd4164dcefc1`，catalog 仍为 revision `13`、SHA-256 `5b022cd3ee07ee7efb90faf676cbb340daec65247a859fdd618561dd2064c8f2`；根 `library/` 不存在，且其 `1,485` 项 tracked deletion 状态未被 C2 改动。

C2 结论：**service tooling complete；canonical migration not applied；ready_for Evaluator；C3 not started**。

### 6.10 C2 修订：迁移 CLI 完全只读

Planner 根据 Evaluator 写边界反馈收紧合同后，`apply-video-spec-refactor.py` 删除了 catalog apply、block promotion、revision bump、`catalog.write_text` 及其死代码。尽管保留历史文件名，该 CLI 现在只接受两个显式且互斥的操作：

- `--check`：从默认 canonical 或显式 `--library` 读取 catalog，把非权威报告写到 stdout，不写任何文件；
- `--report <path>`：只允许把非权威报告写到所选 library 之外的、父目录已存在的显式路径。

裸调用、同时给两个操作、旧 `--apply`/`--promote` 参数均为 argparse usage error（exit `2`）。任何位于默认 canonical 或显式输入 library 内的 report 目标均拒绝且不会创建文件。`--library` 只改变读取源，不能成为写入授权。

报告对六项和可选 `fallbackIds` 使用深拷贝逐值保留，并以键是否存在区分 fallback 的 missing、空数组与非空数组状态；不默认、不修复、不补前缀、不解析 alias、不去重排序或替换。回归 fixture 明确保留以下顺序和值：`registry-component:marker-highlight`、`legacy-alias`、`registry-component:inline-highlight`。报告函数二次调用相同且输入对象逐值不变。

直接 CLI 文档已同步到 Curated Intake `SKILL.md` 与 `references/library-routing.md`；C2 的 director/registry 投影、capability 边界、revision 14 verifier 和 Visual Director 合同保持不变。未修改 canonical、Schema、`_routing.py`、选择器或派生产物，也未进入 C3。

修订后的 focused 测试为 `22 passed`，其中新增写边界 node IDs 为：

- `test_read_only_refactor_preserves_directing_and_fallback_state[False-None]`
- `test_read_only_refactor_preserves_directing_and_fallback_state[True-fallback_value1]`
- `test_read_only_refactor_preserves_directing_and_fallback_state[True-fallback_value2]`
- `test_refactor_cli_requires_one_read_only_operation_and_rejects_removed_mutations`
- `test_refactor_check_cannot_write_default_canonical_catalog`
- `test_refactor_explicit_library_is_read_only_and_report_must_be_outside_it`
- `test_refactor_rejects_report_inside_default_canonical_library`

CLI 测试在每次调用前后同时比较 catalog byte size、SHA-256、`mtime_ns` 和 revision；默认 canonical、显式临时 library、成功 check、成功外部 report 与所有拒绝路径均保持输入 catalog 不变。

```powershell
python -m pytest tests/unit/test_library_tooling_revision14.py
python -m pytest tests/unit/test_library_tooling_revision14.py tests/unit/test_library_schema_revision14.py tests/unit/test_library_routing_contract.py tests/unit/test_talkcraft_director_inventory.py tests/unit/test_visual_director_block_candidates.py
python -m pytest tests/unit
python -m pytest tests/unit --ignore=tests/unit/test_video_spec_handoff_refactor.py
git diff --check
```

| 修订验证 | exit code | 结果 |
| --- | ---: | --- |
| C2 read-only focused | 0 | 22 passed |
| C1/C2 + 相关 library unit | 0 | 71 passed |
| 全 `tests/unit` | 1 | 90 passed / 4 failed / 0 skipped / 0 errors |
| 排除已知 handoff 文件 | 0 | 90 passed |
| `git diff --check` | 0 | 无 whitespace error |

4 个失败仍严格等于第 2 节的既有 handoff node IDs，修订新增失败 `0`。保护复算：canonical `1,575 files / 52,857,763 bytes / 33c40b5947754baec276bbc7e0994d0d8eede72b285d3127f230fd4164dcefc1`；catalog `1,084,951 bytes / revision 13 / 5b022cd3ee07ee7efb90faf676cbb340daec65247a859fdd618561dd2064c8f2`；根 `library/` 不存在，`1,485` 项 tracked deletions 不变。

C2 修订结论：**library CLI read-only boundary complete；ready_for Evaluator recheck；C3 not started**。

### 6.11 C3 catalog：232 项逐项导演语义策展

用户确认 C3 的有界过渡态：`routing` 六项是唯一新导演权威；旧字段在 D 前冻结兼容，不因 revision 14 自动改变 `_routing.py`、palette 选择或排序。C3 不进入 D/E/F。

#### 事务归档与 apply gate

写 canonical 前，完整 Skill library 已归档并实际解包验证：

| 证据 | 值 |
| --- | --- |
| 工作目录 | `C:/Users/buend/AppData/Local/Temp/curated-c3-97236b3f9b2e4f3faf118164ab855029` |
| 恢复归档 | `canonical-library-before.tar` |
| 归档 bytes / SHA-256 | `54,473,728` / `dc7107d996ea197226a9eed602ce87d383e8f01ffd0273670e5a75b97d66ed0d` |
| tar entries | `2,204` |
| 独立 manifest | `pre-c3-manifest.tsv`，`192,174` bytes，SHA-256 `33c40b5947754baec276bbc7e0994d0d8eede72b285d3127f230fd4164dcefc1` |
| 解包恢复复算 | `1,575 files / 52,857,763 bytes / 33c40b...cfc1` |

策展先只发生在仓库外完整 library 副本。Schema、C2 read-only readiness check 与 revision 14 library verifier 全部通过后才 apply；catalog revision 仅由 `13` 提升到 `14` 一次。

#### 逐项语义审计

目标 cohort 恰好 `232`：registry-block `48`、registry-component `123`、svg `31`、lottie `30`。每项均独立编写 `family/purpose/useWhen/avoidWhen/expects/motion`，没有从旧 family、tags、roles 或 kind 做机械映射，也没有用统一文案模板灌入。跨 232 项的 purpose/useWhen/avoidWhen/expects 各有 `232/232/232/232` 个唯一值；placeholder、空字符串、空数组、数组内重复、非法 enum 均为 `0`。

| family | 数量 | family | 数量 |
| --- | ---: | --- | ---: |
| data | 29 | process | 38 |
| structure | 32 | compare | 12 |
| interface | 34 | concept | 24 |
| emphasis | 40 | evidence | 23 |

motion 分布为 entrance-only `36`、progressive `77`、stateful `119`。人工复核后只保留 5 条明确同 family、ready 近邻 fallback：`trace-progress → progress-pill-sweep`、`chart-bar → chart-horizontal-bar`、`flow-sequence → step-chain`、`ui-terminal → ui-code-editor`、`svg:lucide:terminal → svg:command-line`；无其他目标项携带 `fallbackIds`。

结构化前后比较确认：111 个 light assets 与 13 个 out-of-scope 项整项差异 `0`；232 个目标项除六项与 optional fallback 外差异 `0`；catalog 顶层除 revision 外差异 `0`。源文件、TalkCraft 和 provenance 未借策展改写。

#### clean-room 与受控同步

两份全新 source-aware clean-room 各以 `711` 个输入文件开始，并严格按 Registry → aliases → director → director check → legacy verify → library verify → inventory last 执行；每一步 exit `0`。两次完成后均为 `1,575` 文件，逐文件 path/size/SHA 比较 missing `0`、extra `0`、differences `0`。

相对 C3 前 canonical 的受控 delta 为 changed `165`、new `0`、stale `0`：catalog `1`、director catalog `1`、inventory `1`、162 个 Registry `registry-item.json`。`legacy-component-aliases.json`、Registry 总索引/安装文件、两份 provenance report 与 TalkCraft inventory 字节未变，因此没有重写。apply 后 canonical 与 clean-room run 3 逐文件 missing `0`、extra `0`、differences `0`。

TalkCraft inventory 仍为 commit `05691f5f25d91d211f793f5bb0d6941d3ef5723d`、`78` entries、SHA-256 `63248415a4d5619d057fbc380b781fa60254cf820f4e45d4c8bce9bed043beaf`；C3 前后 byte-identical。library 内 4 个 provenance 文件全部 byte-identical。根 `library/` 仍不存在。

新增 `tests/unit/test_library_curation_revision14.py` 用真实 canonical 选择覆盖八个 family、三档 motion、SVG、Lottie、所需 inputs、avoid 条件、5 条人工 fallback，以及 catalog→director→Registry 逐值投影；同时固定 232/111/13 cohort 边界。C2 read-only CLI 与旧路由不变回归继续执行。

#### post-apply 验证

```powershell
python -m pytest tests/unit/test_library_curation_revision14.py tests/unit/test_library_tooling_revision14.py tests/unit/test_library_schema_revision14.py tests/unit/test_library_routing_contract.py tests/unit/test_talkcraft_director_inventory.py tests/unit/test_visual_director_block_candidates.py
python -m pytest tests/unit
python -m pytest tests/unit --ignore=tests/unit/test_video_spec_handoff_refactor.py
python .agents/skills/hyperframes-curated-intake/scripts/apply-video-spec-refactor.py --check
python .agents/skills/hyperframes-curated-intake/scripts/build-director-catalog.py --check
python .agents/skills/hyperframes-curated-intake/scripts/verify-legacy-registry.py --output <outside-library-temp-report>
python .agents/skills/hyperframes-curated-intake/scripts/verify-library-contract.py
python .agents/skills/hyperframes-curated-intake/scripts/inventory-library.py --library .agents/skills/hyperframes-curated-intake/assets/library --output <outside-library-temp-inventory>
git diff --check
```

| 验证 | exit code | 结果 |
| --- | ---: | --- |
| C3/C2/C1 + 相关 library unit | 0 | 85 passed |
| 全 `tests/unit` | 1 | 104 passed / 4 failed / 0 skipped / 0 errors |
| 排除既有 handoff 文件 | 0 | 104 passed |
| C2 canonical readiness | 0 | 232 ready / 0 manual / 0 conflicts，catalog 未写 |
| director check | 0 | checked-in projection byte-current |
| legacy verify | 0 | 临时输出与 checked-in report SHA 均为 `32a93bdf...0665` |
| revision 14 library verify | 0 | 232 complete / 162 Registry ready / 0 errors |
| inventory last | 0 | 临时输出与 checked-in inventory SHA 均为 `839b7bc1...14d4`；summary errors `0` / warnings `19` |
| `git diff --check` | 0 | 无 whitespace error |

4 个失败仍严格等于第 2 节记录的 handoff 基线 node IDs，C3 新增失败 `0`。最终 canonical 为 `1,575 files / 53,098,712 bytes / manifest 9533ba1aedaa3920a765644c0d3d66de278ac677173514f294198330121c50c0`；catalog SHA-256 `a9e3445b30bbec17e1e3ac1495d8a173ef450bb3383c8bfe38182b75f586f596`；director catalog SHA-256 `94a5247c8f5000a73bcde7f302842a556b4e3fd79bace79338fb3cc74e3c0fd2`；inventory SHA-256 `839b7bc10b4527be647fc17b3742b190ee555d064ab0f0774d8f08daa2aa14d4`。

C3 结论：**232-item curation complete；revision 14 deterministic projections current；ready_for Evaluator；D not started**。

### 6.12 D1 types/contracts：revision 15 单一导演契约

用户确认 D 阶段的有界过渡态：revision 15 的 `routing` 六字段是唯一新导演决策权威；revision 14 与 curation v4 仅作为 D2 前迁移输入。D1 只定义 types/contracts，不修改 runtime、canonical catalog、派生产物或 Storyboard v2。

`schemas/library.schema.json` 在不放松 revision 14 的前提下新增 revision 15 条件：`registry-block`、`registry-component`、`svg`、`lottie` 的 `routing` 必须且只允许 `family/purpose/useWhen/avoidWhen/expects/motion` 与 optional `fallbackIds`。revision 15 的目标项拒绝以下旧 top-level 决策字段：`semantic_tags/narrative_roles/granularity/selection_role/motionHooks/supports/compatibleRecipes/affordances/avoid/heroEligible`；同时拒绝旧 routing 字段：`teachingIntents/cognitiveActions/sceneRoles/evidenceTypes/requiredInputs/styleFit/aspectFit/densityFit/containerCost/heroEligible/avoid/durationMin/durationMax`。非决策事实仍保留。

`expects` 只描述导演层语义预期；精确机器输入继续以条目的 `parameters` 或 `interface` 为事实源。hero 是由 purpose/useWhen 等表达的语义，不再存在 `heroEligible` 布尔决策开关。

curation state 增加 `hyperframes-curated-intake/v5` 合同。每个 candidate audit 严格只接受 `id/semanticTier/matchedFamily/matchedUseWhen/matchedPurpose/avoidConflicts/expectsEvidence/hardFilterResults/motionPreference/repetitionApplied/fallbackTrace/source`，`additionalProperties: false`，因此拒绝数值 `score` 及 `matchedSemanticTags/matchedNarrativeRole/selectionRole/granularity`。公共 need 结构只定义一次，v4/v5 仅分别收紧 candidate item；v4 的旧 score/provenance 形状只为 D2 runtime 迁移保留。最初把现行 v4 直接切换为新形状会造成 7 个非 D1 workflow 回归，因此未把 runtime 变更偷渡进 types sprint，而是以显式 v5 版本化边界解决。request/result schema 未复制 candidate audit；它们不承载该状态，故无需修改。

Storyboard v2 的结构和字节完全不变，SHA-256 仍为 `570de77e000465fdc14839203b31e57ebbf2e6ef036153a795592db09d16d824`。request schema SHA-256 `f956a87cf38b26507ea265789b99f826e11f22ec85c1412589f341f45ab50833`、result schema SHA-256 `d5a7145c777287b5e4ed510f21177f5e409100950f8ed208b0aec0318f9189eb`，D1 均未修改。

新增 `tests/unit/test_library_schema_revision15.py` 覆盖：当前 revision 14 catalog 仍可读；revision 15 目标 routing 仅七项；23 个旧字段逐一出现均失败；family/motion 与六项 shape 复用严格合同；非决策事实保留；`expects` 与 `parameters/interface` 分层；无 `heroEligible`；v5 新 audit 通过且五个旧 audit 字段逐一失败；v4 migration input 继续通过；Storyboard v2 hash/结构不变。

```powershell
python -m pytest tests/unit/test_library_schema_revision15.py
python -m pytest tests/unit/test_library_schema_revision15.py tests/unit/test_curated_intake_workflow.py tests/unit/test_curated_routed_mode.py
python -m pytest tests/unit/test_library_schema_revision15.py tests/unit/test_library_schema_revision14.py tests/unit/test_library_curation_revision14.py tests/unit/test_library_tooling_revision14.py tests/unit/test_library_routing_contract.py
python -m pytest tests/unit
python -m pytest tests/unit --ignore=tests/unit/test_video_spec_handoff_refactor.py
git diff --check
```

| 验证 | exit code | 结果 |
| --- | ---: | --- |
| D1 focused | 0 | 34 passed |
| D1 + current workflow compatibility | 0 | 43 passed |
| D1/C3/C2/C1 related | 0 | 110 passed |
| 全 `tests/unit` | 1 | 138 passed / 4 failed / 0 skipped / 0 errors |
| 排除既有 handoff 文件 | 0 | 138 passed |
| `git diff --check` | 0 | 无 whitespace error |

4 个失败仍严格等于第 2 节既有 handoff node IDs，D1 新增失败 `0`。canonical 保护复算为 `1,575 files / 53,098,712 bytes / manifest 9533ba1aedaa3920a765644c0d3d66de278ac677173514f294198330121c50c0`；catalog 仍为 revision `14`、SHA-256 `a9e3445b30bbec17e1e3ac1495d8a173ef450bb3383c8bfe38182b75f586f596`；director 与 inventory SHA 分别保持 `94a5247c8f5000a73bcde7f302842a556b4e3fd79bace79338fb3cc74e3c0fd2`、`839b7bc10b4527be647fc17b3742b190ee555d064ab0f0774d8f08daa2aa14d4`。根 `library/` 仍不存在。

D1 结论：**revision 15 types/contracts complete；canonical/runtime unchanged；ready_for Evaluator；D2 not started**。

### 6.13 D2 runtime：六字段路由与无权重审计

用户裁决已经落实到 runtime：`expects` 只作为导演语义解释与审计证据，不参与 `available_inputs` 集合比较；机器 required input 只来自 `parameters.required` 和 `interface.props[].required=true`。D2 没有修改 canonical、library Schema、Storyboard v2 模型或任何派生产物，也未进入 D3。

`_routing.py` 的非显式选择改为固定 lexicographic 层级：`family → useWhen → purpose → 超过 3 秒的 motion preference → prior-use → ID`。该顺序只比较结构化字段和集合/布尔事实，没有数值 score；任何后层都不能击败更高层。已知 `avoidWhen` 冲突硬排除，未评价的 avoid 保留为 unknown。机器门禁固定检查 status、license、source、声明与实际 source SHA-256、integration/render-time network、Registry installability、`aspectSupport`、dimensions、实际 duration/fps 和 `parameters/interface` required inputs。

`hero_required` 不再读取 top-level 或 routing `heroEligible`；候选必须是 `family=emphasis`，并由非空且与结构化请求相符的 purpose/useWhen 支持，否则形成 miss。可用的显式 catalog ID、SVG 与 logo 锁只做同一组硬门禁，不参与排名。显式 disabled ID 只能按其 `fallbackIds` 声明顺序逐个做完整门禁，首个合格项胜出；无合格 fallback 时 miss。TalkCraft 显式锁原样透传，candidate metadata 保持空，不合成 catalog routing，也不与 catalog 候选混排。

Curated Intake 现在生成 `hyperframes-curated-intake/v5`。candidate audit 严格为 D1 的 `semanticTier/matchedFamily/matchedUseWhen/matchedPurpose/avoidConflicts/expectsEvidence/hardFilterResults/motionPreference/repetitionApplied/fallbackTrace/source`，不生成 score、旧 semantic/narrative/role/granularity 或 repetition 数值。Storyboard 本身不承载 audit。61 个 primitive（31 SVG + 30 Lottie）与 171 个 Registry routed visual 使用相同六字段路径；staging 仍以显式 selected ID 与 hash receipt 为准。

生产选择路径 `_routing.py`、`select-project-palette.py`、`_capabilities.py`、`apply-video-spec-refactor.py`、`build-registry-view.py` 与 `verify-library-contract.py` 已停止读取或生成 23 个旧 catalog/audit 决策字段。`_capabilities.enrich` 现在只补充客观 `capabilities`；只读 migration report 不再从旧 required-input 或 motion 字段提出六项建议。Registry geometry 使用 top-level `aspectSupport/duration` 事实。curation need 上保留的 `affordances` 是既有 D1 state-shape 字段，不是 catalog candidate 决策输入，选择器固定输出空数组。

TalkCraft inventory 本身保持 byte-identical。D2 后的 in-memory director build 直接逐项透传 TalkCraft inventory，不再复造历史 enrichment；因此当前 revision 14 checked-in director projection 中的历史 TalkCraft enrichment 将由 D3 canonical migration 统一清理，D2 遵守“不写 canonical”边界，没有提前重建或改写该文件。

新增 `tests/unit/test_library_routing_revision15.py` 覆盖：旧字段扰动结果不变、新六字段扰动生效；family/useWhen/purpose 的严格层级；长镜头 motion 与 prior-use 不越级；全部机器事实门禁；实际 source byte hash；`expects` 与机器输入分层；avoid known/unknown；semantic Hero；显式 component/SVG/logo；disabled fallback 顺序与 miss；v5 audit Schema/无 score/幂等；61 primitives 与 SVG/Lottie staging；TalkCraft 透传；hidden-aware production scan零旧字段命中。

```powershell
python -m pytest tests/unit/test_library_routing_revision15.py
python -m pytest tests/unit/test_library_routing_revision15.py tests/unit/test_library_schema_revision15.py tests/unit/test_curated_intake_workflow.py tests/unit/test_curated_routed_mode.py tests/unit/test_library_routing_contract.py tests/unit/test_library_tooling_revision14.py
python -m pytest tests/unit
python -m pytest tests/unit --ignore=tests/unit/test_video_spec_handoff_refactor.py
git diff --check
```

| 验证 | exit code | 结果 |
| --- | ---: | --- |
| D2 focused | 0 | 21 passed |
| D2/D1 + workflow/tooling related | 0 | 93 passed |
| 全 `tests/unit` | 1 | 159 passed / 4 failed / 0 skipped / 0 errors |
| 排除既有 handoff 文件 | 0 | 159 passed |
| hidden-aware production old-field scan | 0 | `_routing/_capabilities/apply/build-registry/verify/palette` 命中 0 |
| `git diff --check` | 0 | 无 whitespace error |

4 个失败仍严格等于第 2 节既有 handoff node IDs，D2 新增失败 `0`。保护复算：canonical `1,575 files / 53,098,712 bytes / manifest 9533ba1aedaa3920a765644c0d3d66de278ac677173514f294198330121c50c0`；catalog 仍是 revision `14`、SHA-256 `a9e3445b30bbec17e1e3ac1495d8a173ef450bb3383c8bfe38182b75f586f596`；director、inventory、TalkCraft SHA 分别保持 `94a5247c8f5000a73bcde7f302842a556b4e3fd79bace79338fb3cc74e3c0fd2`、`839b7bc10b4527be647fc17b3742b190ee555d064ab0f0774d8f08daa2aa14d4`、`63248415a4d5619d057fbc380b781fa60254cf820f4e45d4c8bce9bed043beaf`。Storyboard v2 Schema SHA 仍为 `570de77e000465fdc14839203b31e57ebbf2e6ef036153a795592db09d16d824`；根 `library/` 仍不存在。

D2 结论：**runtime routing complete；v5 audit active；canonical/Schema/Storyboard unchanged；ready_for Evaluator；D3 not started**。

### 6.14 D2 最小修订：catalog Schema 预检与 integration fail-closed

按 Planner 修订，`load_catalog()` 现在每次返回前都用仓库唯一权威 `schemas/library.schema.json` 对完整 `catalog.json` 执行 Draft 2020-12 校验。失败作为 configuration error 终止，并逐项报告 `entry`、catalog JSON `path` 与 `field`；没有创建 Skill 内 Schema 副本，也未修改权威 Schema。

`_routing.py` 的 integration 门禁改为 fail-closed：required 字段、允许属性、`mode` enum 和 `timelineOwner` enum 全部从同一 Schema 派生，runtime 测试逐集合断言与 Schema 完全一致。只有精确三字段对象可以通过；missing、unknown、null、empty、numeric、boolean、object 与 array 等无效形状均拒绝。`renderTimeNetwork` 只接受 literal `False`，实现中不再使用 truthy 或 `is not True` 判定。本修订没有改变 ranking、audit、Storyboard、canonical catalog、Schema 或派生产物，也未进入 D3。

```powershell
python -m pytest tests/unit/test_library_routing_revision15.py tests/unit/test_curated_intake_workflow.py -q
python -m pytest tests/unit/test_library_routing_revision15.py tests/unit/test_library_schema_revision15.py tests/unit/test_curated_intake_workflow.py tests/unit/test_curated_routed_mode.py tests/unit/test_library_routing_contract.py tests/unit/test_library_tooling_revision14.py -q
python -m pytest tests/unit -q
python -m pytest tests/unit --ignore=tests/unit/test_video_spec_handoff_refactor.py -q
git diff --check
```

| 验证 | exit code | 结果 |
| --- | ---: | --- |
| loader/integration focused | 0 | 61 passed |
| D2/D1 + workflow/tooling related | 0 | 125 passed |
| 全 `tests/unit` | 1 | 191 passed / 4 failed / 0 skipped / 0 errors |
| 排除既有 handoff 文件 | 0 | 191 passed |
| `_curation.py` / `_routing.py` compile | 0 | 通过 |
| truthy / `is not True` scan | 0 | 命中 0 |
| `git diff --check` | 0 | 无 whitespace error |

全量失败仍严格等于第 2 节既有 4 个 handoff node IDs，本修订新增失败 `0`。保护复算仍为 canonical `1,575 files / 53,098,712 bytes / manifest 9533ba1aedaa3920a765644c0d3d66de278ac677173514f294198330121c50c0`；catalog、director、inventory、TalkCraft SHA-256 分别保持 `a9e3445b30bbec17e1e3ac1495d8a173ef450bb3383c8bfe38182b75f586f596`、`94a5247c8f5000a73bcde7f302842a556b4e3fd79bace79338fb3cc74e3c0fd2`、`839b7bc10b4527be647fc17b3742b190ee555d064ab0f0774d8f08daa2aa14d4`、`63248415a4d5619d057fbc380b781fa60254cf820f4e45d4c8bce9bed043beaf`；根 `library/` 仍不存在。D2 最小修订结论：**full-catalog configuration validation active；integration fail-closed and Schema-derived；ready_for Evaluator；D3 not started**。

### 6.15 D3：revision 15 canonical 迁移

#### 事务归档与恢复验证

D3 写 canonical 前将完整 rev14 library 归档到 workspace 外：

| 证据 | 值 |
| --- | --- |
| 工作目录 | `C:/Users/buend/AppData/Local/Temp/curated-d3-26ecfcfed1cf42f78d9161ccf2ec4fe8` |
| 恢复归档 | `canonical-rev14-recovery.tar` |
| archive bytes / SHA-256 | `54,724,608` / `ca64cd0f8b50ae04ca96a3799ffd1ff7accc779dd771342a37ca44086d124b08` |
| tar entries | `2,204` |
| rev14 source manifest | `1,575 files / 53,098,712 bytes / 9533ba1aedaa3920a765644c0d3d66de278ac677173514f294198330121c50c0` |
| 实际解包复算 | `1,575 files / 53,098,712 bytes / 9533ba1aedaa3920a765644c0d3d66de278ac677173514f294198330121c50c0` |

归档及解包后的完整恢复副本至少保留到 Evaluator PASS。

#### 精确字段迁移与机器事实保全

迁移只把 catalog revision 从 `14` 提升到 `15` 一次，并从所有 356 个 entry 的适用层级删除合同列出的旧决策字段。删除总计 `4,778` 个字段实例：top-level `2,528`，routing `2,250`。

| 层级 | 字段计数 |
| --- | --- |
| top-level | `semantic_tags 356`、`narrative_roles 356`、`granularity 356`、`selection_role 356`；`motionHooks/supports/compatibleRecipes/affordances/avoid/heroEligible` 各 `184` |
| routing | `teachingIntents/cognitiveActions/sceneRoles/evidenceTypes/requiredInputs/styleFit/aspectFit/densityFit/containerCost/heroEligible/avoid` 各 `174`；`durationMin/durationMax` 各 `168` |

第一次 clean-room 暴露 10 个 ready Registry Block 的客观机器事实此前仅由旧 routing 或旧派生 Registry item 承载，D2 的 top-level-only generator 因而只能映射 `152/162`。为保证 fail-closed 门禁且不保留旧决策字段，迁移将客观事实显式放回现有非决策字段：8 个缺 viewport/dimensions 声明的 Block 增加 `aspectSupport: ["16:9"]`；两个缺 duration 声明的 code-snippet Block 增加 `duration: 7` 与 `duration: 12`。值分别来自迁移前 routing aspect 与已归档 Registry 的确定性 geometry/duration，没有修改六字段语义。

232 个目标的 `family/purpose/useWhen/avoidWhen/expects/motion` 与 optional `fallbackIds` 逐值投影在迁移前后完全相等，规范化投影 SHA-256 均为 `51764659392a2d5a1b25a2051aa0e776e3086f4327265276046fb47f0d2d5cf6`。111 个轻量资产和 13 个 out-of-C 项除移除旧字段及上述明确的 Block 机器事实补全外，其余结构逐值保留。

#### 双 clean 生成、apply delta 与回归

规范化后的两个完整 clean-room 严格按 `registry → aliases → director → director check → legacy verify → library verify → inventory last` 顺序运行，全部命令 exit `0`。两份结果均为 `1,575` 文件，path/size/SHA missing `0`、extra `0`、differences `0`。相对 rev14 canonical 的确定性 delta 仅 `3 changed / 0 new / 0 stale`：

- `catalog.json`
- `director-catalog.json`
- `inventory-latest.json`

canonical apply 后与 clean-room 完整逐文件比较 differences `0`。legacy aliases、Registry 162 项及两个 provenance 派生报告 byte-identical，无需重写。post-apply director check、legacy byte compare、revision 15 library contract（232/232 complete、162/162 installable）和 inventory byte compare均通过。

TalkCraft source inventory 仍 byte-identical 且固定为 78 entries。D2 已把 director builder 改为 TalkCraft 原样透传，D3 重建因此清除了旧 director projection 曾对其中 10 项合成的五类 catalog 决策字段，并把这 10 项的 `avoid` 恢复为 inventory 原值；当前 director 的 78 个 TalkCraft entries 与 `talkcraft-inventory.json#entries` 逐值完全相等。该变化只发生在允许重建的 `director-catalog.json`，没有改写 TalkCraft inventory、ID、card 集、hash、commit 或 source。

真实 selector 在迁移前后使用同一 approved Storyboard：两次均生成 70 个 lane-specific needs、27 个唯一 selected IDs、0 miss，selected ID 顺序完全一致；revision 15 clean-room 在派生前也独立通过完整 Schema loader 与 selector。

最终 canonical 为 `1,575 files / 52,489,179 bytes / manifest 7b0cd5d3a659969de670141ede72da1a63f93dd68884dcf1d30c09ca079d1103`。关键 SHA-256：catalog `8ee24dd0d01e8199ed54d44fb990663205ccfc3e210dafbc227a64259a480809`；director `4df57226de131dfa9e5b1c5fdf036da70f4765a6a3cf6aa53a384ce30adf914f`；inventory `bc4824a0b03ac593c175efcebebe6d9311bd32af49a81224f8b62061d058abfe`。TalkCraft 保持 `63248415a4d5619d057fbc380b781fa60254cf820f4e45d4c8bce9bed043beaf`，candidate manifest 保持 `9226b83d5f8c7541061bfc99cf559a91176209b2cb61d1eed99cec0a8f6440d8`；当时仍存在的 `provenance/curated-library-inventory.json`（SHA `be64e3279623bbbf9558ae231252d2d2d7443dc955157c783e3769c6faaf7f13`）已在 F1 作为 stale revision 7 snapshot 移除；根 `library/` 仍不存在。

结构化 hidden-aware gate 确认 canonical 356 个 catalog entry 的 top/routing 旧字段命中 `0`，对应 director catalog projection 与 Registry routing 同样为 `0`。TalkCraft 原始 inventory 和 catalog entry 内非决策 provenance 子对象不属于该字段层级且保持冻结；生产脚本唯一同名 `affordances` 是 curation v5 need 的既有空数组字段，不是 catalog 分类或权重。

```powershell
python -m pytest tests/unit/test_library_schema_revision15.py tests/unit/test_library_schema_revision14.py tests/unit/test_library_curation_revision14.py tests/unit/test_library_tooling_revision14.py tests/unit/test_library_routing_contract.py tests/unit/test_library_routing_revision15.py -q
python -m pytest tests/unit -q
python -m pytest tests/unit --ignore=tests/unit/test_video_spec_handoff_refactor.py -q
git diff --check
```

| 验证 | exit code | 结果 |
| --- | ---: | --- |
| D3 schema/catalog/tooling/routing focused | 0 | 165 passed |
| 全 `tests/unit` | 1 | 193 passed / 4 failed / 0 skipped / 0 errors |
| 排除既有 handoff 文件 | 0 | 193 passed |
| production script 旧字段扫描 | 0 | 命中 0 |
| canonical/director entry 层结构化旧字段扫描 | 0 | `0 / 0` |
| `verify-library-contract.py` compile | 0 | 通过 |
| `git diff --check` | 0 | 无 whitespace error |

全量 4 个失败仍严格等于第 2 节既有 `test_video_spec_handoff_refactor.py` node IDs，D3 新增失败 `0`。Storyboard v2 Schema SHA-256 仍为 `570de77e000465fdc14839203b31e57ebbf2e6ef036153a795592db09d16d824`。

D3 结论：**revision 15 canonical applied；deterministic derived views current；TalkCraft/provenance/candidates/sources protected；ready_for Evaluator；E/F not started**。

### 6.16 E1：Storyboard v3 types-only 合同

E1 将 `references/storyboard-spec.schema.json` 设为未来 canonical
`hyperframes-storyboard/v3` Schema。根字段为 `schema/title/duration/timing_mode/scenes`，仅
`message` 可选；scene 必备 `id/start/end/content/visual/uses/motion`，并只允许可选
`title/next/narration/on_screen_text/sfx/source_anchor/locks`。Schema 不接受 v2 的
`creative_profile/throughline`，也不接受 selector、百分比事件、候选 audit、approval 或
needs-review 状态。

`uses` 的唯一结构是 `{id,responsibilities,required}`：ID 必须为 catalog 或 `authored:`
格式，职责数组非空且唯一，`required` 必须为 boolean，同一 scene 中 ID 唯一。`next` 只含
相邻 `sceneId` 与非空 transition 语义；普通硬切可省略，末镜必须省略。纯验证器另外执行
Schema 无法表达的 scene ID 唯一、正时间窗、连续覆盖 `0..duration`、相邻 next、uses ID
唯一，以及全局 locked timing 和 scene locks 的 patch 保护。locks 仅允许 timing、content、
visual、uses、motion、next 六个 boolean。

`curated-intake-result.schema.json` 已定义 `hyperframes-visual-director/curated-result-v3`，
scene patch 通过 canonical v3 Schema 的 `$defs/scenePatch` 复用字段事实源，不允许 v2 patch
字段。原 Storyboard v2 Schema 原样冻结为 `storyboard-spec.v2.legacy.schema.json`；E1 当时冻结的
routed v2 packet Schema `curated-intake-result.v2.legacy.schema.json` 已在 F1 因零 consumer 移除；现有 `_curation.py`
显式读取该 frozen 文件，故 E1 生产 intake/renderer/handoff 和 routed v2 output 行为保持
不变。E1 没有 migration、runtime cutover、项目 artifact 重写或 approval 继承。

Schema SHA-256：frozen Storyboard v2
`570de77e000465fdc14839203b31e57ebbf2e6ef036153a795592db09d16d824`；canonical Storyboard v3
`cd418cd4ae147163aaed540f929f3add6492ad9eb22363399fbbc47ce22b4e2e`；routed result v3
`72b7a63c77d210049faaceda442d22c3b0ec68021746ea9ed7862eaba071c32e`。

```powershell
python -m pytest tests/unit/test_storyboard_schema_v3.py tests/unit/test_curated_intake_workflow.py tests/unit/test_curated_routed_mode.py tests/unit/test_library_schema_revision15.py -q
python -m pytest tests/unit -q
python -m pytest tests/unit --ignore=tests/unit/test_video_spec_handoff_refactor.py -q
python -m py_compile .agents/skills/hyperframes-curated-intake/scripts/_storyboard_v3_contract.py .agents/skills/hyperframes-curated-intake/scripts/_curation.py
git diff --check
```

| 验证 | exit code | 结果 |
| --- | ---: | --- |
| E1 Schema/patch + v2 runtime focused | 0 | 86 passed |
| 全 `tests/unit` | 1 | 234 passed / 4 failed / 0 skipped / 0 errors |
| 排除既有 handoff 文件 | 0 | 234 passed |
| v3 contract / frozen-v2 loader compile | 0 | 通过 |
| `git diff --check` | 0 | 无 whitespace error |

全量失败仍严格等于第 2 节四个既有 handoff node IDs，E1 新增失败 `0`。canonical library
仍为 `1,575 files / 52,489,179 bytes`，根 `library/` 不存在；E1 未触碰 canonical library、
项目 artifacts、Storyboard approval、TalkCraft、provenance、candidate 或任何派生库文件。

E1 结论：**v3 types and pure lock validation ready；v2 runtime frozen and unchanged；ready_for
Evaluator；E2 migration/runtime cutover not started**。

#### E1 最小修订：catalog namespace 与根 Schema 对齐

Evaluator 发现 canonical Library Schema 的 kind enum 还包含 `template`。v3
`catalogOrAuthoredId` 已补入该 namespace，并把 suffix 收紧为小写 ID 语法。测试不再手抄
namespace 清单，而是动态读取仓库根唯一 `schemas/library.schema.json` 的 entry kind enum：每个
`<kind>:example` 及 `authored:example` 必须通过，接受的 catalog namespace 集合必须与根 enum
完全一致；`unknown:example`、`template:`、`:example`、无 namespace 以及 namespace/suffix
大小写错误必须拒绝。本修订没有修改根 Schema、runtime、catalog、迁移器或 E2 内容。

修订后 Storyboard v3 Schema SHA-256 为
`cd418cd4ae147163aaed540f929f3add6492ad9eb22363399fbbc47ce22b4e2e`；focused 为 `86 passed`，
全 unit 为 `234 passed / 4 known failed`，排除既有 handoff 文件为 `234 passed`；
`git diff --check` exit `0`。四个失败 node IDs 未变，新增失败 `0`。

### 6.17 E2：显式 v2→v3 迁移与 production v3-only cutover

E1 已由 Evaluator 判定 **PASS** 后才进入本阶段。E2 没有迁移任何真实项目，也没有继承
approval 或 locks。新增 `migrate-storyboard-v2-to-v3.py` 要求显式且互异的 `--input`、
`--output`、`--report`；原地迁移、v3 输入和非 v2 输入全部拒绝。相同 v2 输入两次生成的
v3 draft 与外置 report 分别 byte-identical，report 固定为 `needs-review`、
`authoritative:false`、`approvalInherited:false`，不含时间戳或绝对路径，因此不是第二权威。

迁移逐镜保留 scene ID、title、takeaway→content、三项 visual thesis 与一到两项 focus 的
固定标签文本、source anchor，以及 choreography 中每个 event 的 change/purpose 原顺序。
event id 只进入 report 映射证据，不进入 Storyboard；event window/target/role 均被删除。
`uses` 按 event.via→reuse.id→exit.via 的首次出现顺序稳定聚合，职责稳定去重、任一来源
required 即为 true；event.via 是最终显式 binding，固定 required；exit.via 职责明确标为
transition。非末镜 `next` 保留 exit.to_scene/state，末镜 state 保留到 motion；migration 不写
locks、approval、selector、百分比或 candidate audit。report 同时记录 root、scene ID、全部
文本、event、binding 和 source-anchor 指针映射，足以审计没有静默丢失。

Production runtime 现只接受 `hyperframes-storyboard/v3`：`_curation`、renderer、compiled
cache、manifest、prepare、selector、staging 与 handoff/build verification 均读取数字
start/end、content/visual/motion/uses/next。v2 输入 fail-fast，并输出可直接识别的显式
`migrate-storyboard-v2-to-v3.py --input ...` 指令；没有 implicit migration。该轮曾以 motion
标签作为长镜头审查门禁；6.19 的第二次最小修订已明确取代此实现，改为外置、exact-hash、
逐 scene 的结构化 reviewer confirmation。

Selector 以 scene `uses` 作为最终 binding，并用 content/visual/motion/responsibilities 形成
语义 query；required catalog binding 不可用时立即失败，optional 不可用时保留在
`catalogMisses`，handoff verification 继续输出 `optional-use-miss` warning。机器 staging 只
要求 required、非 authored uses。staging receipt、compiled Storyboard、manifest、handoff 与
verification report 均升级到 v3；旧 creative 字段不能绕过 compiled Schema 或 manifest gate。

Routed result 升级为 `hyperframes-visual-director/curated-result-v3`，patch 仅允许 v3 scene
字段。Visual Director request v2 的 `approvedScope.segmentSceneMap` 提供 stable scene ID 映射，
同一 ID 不可重复分配；映射与 Storyboard scene 集必须完全一致。merge 同时执行 parent hash、
segment scope、request scene locks、现有 scene locks 和不可清锁保护。Visual Director compile
从已有 `storyboardScenes` 派生 stable mapping/locks；没有把 curation audit 写回 Storyboard。
`approvedScope.segmentSceneMap` 因此以 stable scene ID 驱动合并，不依赖镜头顺序或旧
event ID。

E2 runtime 使用真实 canonical ID 时暴露 E1 suffix 过窄：例如
`svg:primitive:document` 的合法 kind-relative ID 需要嵌套冒号。v3 Schema 仅把 suffix 从单层
小写 ID 放宽为仍然小写、非空且 namespace 严格的嵌套 suffix；根 kind namespace 集仍与
`schemas/library.schema.json` enum 完全一致，empty namespace/suffix、unknown 和大小写错误
继续拒绝。最终 Storyboard v3 Schema SHA-256 为
`8b35cf661db527634feeb860dd6137effb13dc6c890306ad241772f0e134a131`；frozen v2 Schema 仍为
`570de77e000465fdc14839203b31e57ebbf2e6ef036153a795592db09d16d824`，routed result v3 Schema
仍为 `72b7a63c77d210049faaceda442d22c3b0ec68021746ea9ed7862eaba071c32e`。

保护门禁：E2 未修改 `.agents/skills/hyperframes-curated-intake/assets/library/**`。canonical
保持 `1,575 files / 52,489,179 bytes`，catalog/director/inventory/TalkCraft SHA-256 分别为
`8ee24dd0d01e8199ed54d44fb990663205ccfc3e210dafbc227a64259a480809`、
`4df57226de131dfa9e5b1c5fdf036da70f4765a6a3cf6aa53a384ce30adf914f`、
`bc4824a0b03ac593c175efcebebe6d9311bd32af49a81224f8b62061d058abfe`、
`63248415a4d5619d057fbc380b781fa60254cf820f4e45d4c8bce9bed043beaf`；根 `library/` 仍不存在。
D 路由/catalog、真实项目 artifact、approval、TalkCraft 与 provenance 均未改。

```powershell
python -m pytest tests/unit/test_storyboard_migration_v2_to_v3.py tests/unit/test_curated_intake_workflow.py tests/unit/test_curated_routed_mode.py tests/unit/test_storyboard_schema_v3.py tests/unit/test_library_routing_contract.py tests/unit/test_visual_director.py -q
python -m pytest tests/unit -q
python -m pytest tests/unit --ignore=tests/unit/test_video_spec_handoff_refactor.py -q
python -m compileall -q .agents/skills/hyperframes-curated-intake/scripts .agents/skills/hyperframes-visual-director/scripts
git diff --check
```

| 验证 | exit code | 结果 |
| --- | ---: | --- |
| E2 migration/runtime/routed/VD focused | 0 | 71 passed |
| 全 `tests/unit` | 1 | 240 passed / 4 failed / 0 skipped / 0 errors |
| 排除既有 handoff 文件 | 0 | 240 passed |
| Curated + Visual Director scripts compile | 0 | 通过 |
| hidden-aware production v2/old scene-field scan | 0 | 仅显式 migration、frozen guard 与 manifest 禁止字段命中 |
| `git diff --check` | 0 | 无 whitespace error |

全 unit 的四个预期失败仍须严格等于第 2 节既有
`test_video_spec_handoff_refactor.py` node IDs；E2 新增失败必须为 `0`。E2 结论：
**explicit migration complete；production v3-only；real project migration/approval remains E3；
ready_for Evaluator；F not started**。

### 6.18 E2 最小修订：migration-only recipe、exact review 与严格 routed membership

Evaluator 修订未改变 E2 已通过的 v3 runtime、staging、compiled、manifest、result 或 D 路由
行为，只收紧四个边界。

1. Storyboard v3 use ID 被拆为 `catalogOrAuthoredUseId`、
   `migrationOnlyRecipeUseId` 与其 union `useId`。前者的 catalog namespace 仍与根
   Library Schema kind enum 完全一致；`recipe:` 不加入 Library enum，也不成为 catalog kind。
   v2 migration 对 event.via、reuse.id 与 exit.via 的 recipe ID、职责、顺序和 required-OR
   逐值保留。Selector 可在 migration review curation 中暴露它；approved selector、prepare、
   staging 与 handoff verification 均 fail closed，且不改成 authored、不解析 alias、不猜替代。
2. Selector 的 query 是 Unicode 原文按固定顺序拼接：`content → visual → motion → 当前 use.id
   → responsibilities 数组顺序`。任一权威字段、ID 或职责顺序变化都会改变 query；title、
   v2 字段和 candidate audit 不参与。
3. Routed request 的 `segmentSceneMap` keys 必须精确等于 requested segment 集，scene ID 全局
   唯一归属，空数组明确表示该 segment 无 scene，`sceneLocks` 只能引用映射内 ID。
   `_routed` 已删除单 segment fallback；Storyboard scenes 与映射集合必须完全相等。
   Visual Director merge 现在强制要求原 request，并在修改前拒绝 unknown、duplicate、
   cross-segment scene patch。
4. Migration 不再插入 motion 模板，只按原序保留 v2 change/purpose，并在 report 逐 scene
   标为 unresolved。`--review-report` 只允许审阅 migration draft；生产 selection 必须读取外置
   `--review-confirmation`。Curation v5 保存 exact Storyboard hash、reviewer confirmation、逐长镜头
   decision 与结构化 evidence；prepare、stage、handoff 复验同一份证据。长度、关键词或 motion
   前缀均不能作为通过依据。

最终 Storyboard v3 Schema SHA-256 为
`7a017051669015fd873549681c2607892cebc8378abd23ff74e681438033ed15`，curation Schema 为
`0327db000a9e77f1efe723ca41aab6248cf53015f1983e8f256824ba376291a2`；frozen v2 Schema 仍为
`570de77e000465fdc14839203b31e57ebbf2e6ef036153a795592db09d16d824`。

```powershell
python -m pytest tests/unit/test_storyboard_migration_v2_to_v3.py tests/unit/test_curated_intake_workflow.py tests/unit/test_curated_routed_mode.py tests/unit/test_storyboard_schema_v3.py tests/unit/test_library_routing_contract.py tests/unit/test_visual_director.py tests/unit/test_library_routing_revision15.py -q
python -m pytest tests/unit -q
python -m pytest tests/unit --ignore=tests/unit/test_video_spec_handoff_refactor.py -q
python -m compileall -q .agents/skills/hyperframes-curated-intake/scripts .agents/skills/hyperframes-visual-director/scripts
git diff --check
```

| 验证 | exit code | 结果 |
| --- | ---: | --- |
| E2 revision + D routing guard focused | 0 | 130 passed |
| 全 `tests/unit` | 1 | 246 passed / 4 failed / 0 skipped / 0 errors |
| 排除既有 handoff 文件 | 0 | 246 passed |
| Curated + Visual Director scripts compile | 0 | 通过 |

canonical library 仍为 `1,575 files / 52,489,179 bytes`；catalog、director、inventory、
TalkCraft SHA-256 仍分别为 `8ee24dd0d01e8199ed54d44fb990663205ccfc3e210dafbc227a64259a480809`、
`4df57226de131dfa9e5b1c5fdf036da70f4765a6a3cf6aa53a384ce30adf914f`、
`bc4824a0b03ac593c175efcebebe6d9311bd32af49a81224f8b62061d058abfe`、
`63248415a4d5619d057fbc380b781fa60254cf820f4e45d4c8bce9bed043beaf`；根 `library/`
仍不存在。未修改 Library enum/catalog、D routing、真实项目或 E3 状态。最终结论：
**E2 revision ready_for Evaluator；E3/F not started**。

### 6.19 E2 第二次最小修订：结构化长镜头审核与 recipe 阶段边界

超过 3 秒的镜头不再由 motion 长度、关键词、箭头或 `Internal change:` / `Static reason:` 前缀
通过。生产 selector 只接受外置 `--review-confirmation`：其 SHA 必须精确等于规范化 Storyboard
SHA，并包含非占位 reviewer、总确认，以及每个长镜头恰好一个 sceneId 记录。`internal-change`
证据要求不同的 before/after 和 direction，三项文本均须逐值出现在该镜头 motion 中；
`static-reason` 要求 object/reason 同样对应 motion，并将 reasonType 限定为
`readability/evidence-preservation/timing-lock/source-fidelity/accessibility`。英中占位词、标签前缀
和四条 filler 回归全部拒绝；修改 Storyboard 后复用旧 confirmation 会以 stale hash 失败。
Migration report 永远保持 needs-review，绝不自动生成 decision 或 evidence。

Recipe 阶段边界现在区分三种结果：既有 legacy resolver 映射到真实 catalog ID 时记录
`recipeResolutions` provenance 并按该真实 ID selection/staging；required unresolved recipe 在
selector 立即失败；optional unresolved recipe exit `0`，产生 `reason=unresolved-recipe` 的可见
miss（含 recipe ID、required、sceneId、source/provenance），且不进入 selectedIds 或 staging。
任何仍未解析 recipe 均由 prepare、stage 和 handoff fail closed。

本修订没有修改 canonical library、根 Library Schema、D routing、真实项目或 E3 状态。

```powershell
python -m pytest tests/unit/test_storyboard_migration_v2_to_v3.py tests/unit/test_curated_intake_workflow.py tests/unit/test_curated_routed_mode.py tests/unit/test_library_routing_contract.py tests/unit/test_library_schema_revision15.py -q
python -m pytest tests/unit -q
python -m compileall -q .agents/skills/hyperframes-curated-intake/scripts .agents/skills/hyperframes-visual-director/scripts
git diff --check
```

focused 为 exit `0`、`66 passed`；全 unit 为 exit `1`、`251 passed / 4 failed / 0 skipped /
0 errors`，四个失败仍严格等于第 2 节既有 handoff node IDs，新增失败 `0`。compileall 与
`git diff --check` 均 exit `0`。活动代码/直接测试中 `review-state`、`explicit-human-review`、
`require_reviewed_motion` hidden-aware 命中 `0`。curation Schema SHA-256 为
`7c10f0cddb5c5ebff24b4244247e11c670efc9c6596057855d118f1b4286de58`。

canonical 的 catalog/director/inventory/TalkCraft SHA-256 仍为
`8ee24dd0d01e8199ed54d44fb990663205ccfc3e210dafbc227a64259a480809`、
`4df57226de131dfa9e5b1c5fdf036da70f4765a6a3cf6aa53a384ce30adf914f`、
`bc4824a0b03ac593c175efcebebe6d9311bd32af49a81224f8b62061d058abfe`、
`63248415a4d5619d057fbc380b781fa60254cf820f4e45d4c8bce9bed043beaf`；根 `library/` 不存在。
结论：**E2 second revision ready_for Evaluator；E3/F not started**。

### 6.20 E2 finalized 最小修订：自动 Agent attestation 与 live recipe provenance

本节取代 6.19 中“CLI 判断 filler/语义”和“human confirmation”的实现描述。正常 Curated
Intake / Visual Director Agent 是长镜头语义 authority，不增加用户操作步骤。Agent 按
`motion-attestation/v1` rubric 形成仓库外 attestation；每个超过 3 秒的 scene 记录 exact
Storyboard SHA、sceneId、完整逐字 `motionQuote`、`internal-change|static-reason` decision、
结构化 conclusion、rationale，以及 reviewer `{type=automated-agent, workflow,
rubricVersion, modelId|runProvenance}`。Migration 不生成 attestation。

CLI 只校验 JSON 结构、exact hash、完整 quote、受支持 provenance、长镜头集合精确覆盖、
duplicate/conflict 与 stale；`_curation.py` 已删除 filler/keyword/prefix/length/denylist/substr/NLP
判断。英中合格与 filler/template/same-state/missing-direction/non-specific-static-reason 语义案例
由版本化 `motion-attestation-rubric.md` 和
`tests/fixtures/curated-intake-motion-attestation-v1.json` 作为 Agent-eval oracle，而不是伪装成
CLI 文本分类器。

Selector 的 optional/required recipe 边界保持不变。对已由 legacy aliases 映射的 recipe，
curation claim 现在冻结 resolved ID、catalog revision/hash、aliases hash、逐 source path/hash、
status、license、integration 与 selected-library provenance。prepare、stage、handoff 每次均从
本次 `--library` 现场重读 catalog 与 aliases，唯一重解析并逐值验证 claim、catalog Schema、
source 声明/hash 与 stageability；fabricated、stale、changed、duplicate/conflicting claim 均拒绝。
Staging receipt 在对应真实 catalog item 上原样保留 recipe resolution evidence。

本修订继续冻结 Storyboard Schema、根 Library Schema、canonical library、D routing、真实项目
与 E3。

```powershell
python -m pytest tests/unit/test_storyboard_migration_v2_to_v3.py tests/unit/test_curated_intake_workflow.py tests/unit/test_curated_routed_mode.py tests/unit/test_library_routing_contract.py tests/unit/test_library_schema_revision15.py -q
python -m pytest tests/unit -q
python -m compileall -q .agents/skills/hyperframes-curated-intake/scripts .agents/skills/hyperframes-visual-director/scripts
git diff --check
```

focused 为 exit `0`、`69 passed`；全 unit 为 exit `1`、`254 passed / 4 failed / 0 skipped /
0 errors`，四个失败仍严格等于第 2 节既有 handoff node IDs，新增失败 `0`。compileall 与
`git diff --check` 均 exit `0`。curation Schema SHA-256 为
`e30b6d1f265cd6112b3777a802ee09f785dd0a835abef9c375af813eb686dfdb`。

canonical catalog/director/inventory/TalkCraft SHA-256 仍为
`8ee24dd0d01e8199ed54d44fb990663205ccfc3e210dafbc227a64259a480809`、
`4df57226de131dfa9e5b1c5fdf036da70f4765a6a3cf6aa53a384ce30adf914f`、
`bc4824a0b03ac593c175efcebebe6d9311bd32af49a81224f8b62061d058abfe`、
`63248415a4d5619d057fbc380b781fa60254cf820f4e45d4c8bce9bed043beaf`；根 `library/`
仍不存在。结论：**E2 finalized revision ready_for Evaluator；E3/F not started**。

### 6.21 E2 rubric 最小修订

`curation.schema.json` 与 runtime 共用唯一 production 接受值：精确、大小写敏感的
`motion-attestation/v1`。Selector、prepare、stage、handoff 均在各自边界执行同一验证；
missing、null、empty、大小写变化、前后空白、v0、v2 与随机值全部拒绝，错误同时输出
`actual=<实际值>` 与 `supported='motion-attestation/v1'`。三条 downstream exploit 回归覆盖
prepare/stage/handoff，防止 Schema 校验先行时丢失统一诊断。本修订未改变 attestation 语义
rubric、recipe live provenance、Storyboard/library/D routing 或 E3 状态。

focused rubric/runtime suite 为 exit `0`、`79 passed`；全 unit 为 exit `1`、`264 passed /
4 failed / 0 skipped / 0 errors`，四个失败仍严格等于第 2 节既有 handoff node IDs，新增失败
`0`。compileall 与 `git diff --check` 均 exit `0`。最终 curation Schema SHA-256 为
`24ce227f181c52995595ff682e07a5d731d25f3551a3186630513b7784b9c93b`。canonical 四个关键
hash 与 6.20 相同，根 `library/` 仍不存在。结论：**E2 rubric revision ready_for Evaluator**。

### 6.22 E3：production v3-only 清理与真实项目闭环

E3 移除了最后的生产 v2 适配面：Visual Director routed request 和 compiled packet 现在均为
`hyperframes-visual-director/curated-request-v3`，schema、直接文档和测试同步。显式
`migrate-storyboard-v2-to-v3.py`、明确为 legacy/migration-only 的 frozen v2 Schema、迁移测试
和历史审计继续保留。`load_storyboard_spec` 对 v2 只 fail-fast 并给出显式迁移命令，不做
implicit upgrade 或 compatibility fallback。

最小修订审计：E3 首次实现曾在没有单独删除授权时移除 untracked
`migrate-storyboard-v1-to-v2.py`，现已从删除前会话输出按内容恢复并保持 untracked。删除前没有
保存独立 bytes/hash，因此只能确认 content-equivalent；newline/BOM 和 byte identity 无法证明，
不作虚假声明。该脚本不是 production implicit adapter，是否淘汰留待 F 的引用与授权评估。

新增两个最小 v3 fixture：生产 fixture 覆盖真实 logo/svg/registry component、optional miss、
timing/uses/motion/next locks、普通 hard cut、末镜无 next，以及由自动 Agent attestation 签核的
`internal-change` 与 `static-reason` 长镜头；recipe fixture 固定 migration-only unresolved recipe
边界。fixture 不包含 selector、百分比事件或 audit。

仓库外真实项目目录为
`C:\Users\buend\AppData\Local\Temp\curated-e3-34042c0e0e7940f6953ce320d2bd3e2c`。
使用 canonical revision 15、真实 `biennale-yellow` Frame、catalog 与 registry，实际顺序为 v3
request → selector → routed prepare/result → Visual Director merge → final prepare →
compiled/manifest/STORYBOARD → stage → verify。review 由 automated-agent
`curated-intake/motion-attestation-v1/gpt-e3-fixture` 提供，没有增加用户确认步骤。结果：

- Storyboard object SHA-256 为 `84a0ea21ba21e57cbc4a4bbe5545deb27dc8b10c2247f6190f34d1bc88f82357`；
  三个稳定 scene ID 在 request、result、compiled 与 verification 中闭合。
- selected IDs 精确为 `logo:openai:mark`、`registry-component:active-border`、
  `svg:primitive:document`；`logo:missing-optional` 保持一个可见 optional miss，未 selected/staged。
- staging receipt 为 3 items；logo/svg 单文件及 component 的 3 个 source 文件均逐项
  `sourceHash == destinationHash`。正常 handoff 为 exit `0`、`ok=true`、`errors=0`、`warnings=1`
  （唯一 warning 为 optional miss）。
- 篡改生成后的 `STORYBOARD.md` 再验证为 exit `1`，明确报告 `compiled-stale` 与
  `artifact-hash`，证明 stale cache/manifest 均 fail closed。

```powershell
python -m pytest tests/unit/test_curated_intake_workflow.py tests/unit/test_curated_routed_mode.py tests/unit/test_storyboard_migration_v2_to_v3.py tests/unit/test_storyboard_schema_v3.py tests/unit/test_visual_director.py tests/unit/test_library_routing_contract.py -q
python -m pytest tests/unit -q
python -m compileall -q .agents/skills/hyperframes-curated-intake/scripts .agents/skills/hyperframes-visual-director/scripts
git diff --check
```

focused 为 exit `0`、`95 passed`；全 unit 为 exit `1`、`264 passed / 4 failed / 0 skipped /
0 errors`。失败 node IDs 仍严格等于第 2 节既有四项，E3 新增失败 `0`。hidden-aware 生产扫描
仅剩 `_curation.py` 的显式 v2 fail-fast、两个显式 migration CLI、frozen legacy Schema 与禁止
旧字段的 verification guard；无 production implicit adapter 或 v2 request/result/compiled writer。

canonical library 前后 manifest 均为 `1,575 files / 52,489,179 bytes /
7b0cd5d3a659969de670141ede72da1a63f93dd68884dcf1d30c09ca079d1103`；catalog 与 TalkCraft
SHA-256 分别保持 `8ee24dd0d01e8199ed54d44fb990663205ccfc3e210dafbc227a64259a480809`、
`63248415a4d5619d057fbc380b781fa60254cf820f4e45d4c8bce9bed043beaf`，根 `library/` 仍不存在。
上述临时目录已在记录完成后删除且复验不存在。E3 未修改 canonical library、D routing 或真实
项目，也未进入 F。结论：**E3 ready_for Evaluator；F not started**。

#### E3 最小修订：恢复未获删除授权的 v1→v2 migration

恢复脚本 SHA-256 为 `b28b87fdc72758ed2fb5475e765309ee5b3da99a6a0d80150231defb05bb8d2e`，
并保持 `??` untracked、未执行 `git add`。仓库没有独立 v1→v2 pytest node；因此以脚本
`py_compile` 加一次 v1 fixture→v2 output→frozen v2 Schema validation 复验，exit `0`、1 scene、
Schema errors `0`。E3 focused 仍为 `95 passed`；全 unit 仍为 `264 passed / 4 failed / 0 skipped /
0 errors`，仅四个既有 handoff failures。全脚本 compileall 与 `git diff --check` 均 exit `0`。
hidden scan 将该脚本分类为显式历史 migration，而不是 production adapter；production v2
request/result/compiled writer 仍为 `0`。canonical manifest 与 6.22 相同，根 `library/` 不存在。

### 6.23 F1：双目标有界清理

删除前冻结的精确目标均为 `??` untracked：

| 绝对路径 | bytes | SHA-256 | consumer 结论 |
| --- | ---: | --- | --- |
| `C:\Users\buend\Desktop\mav 3\.agents\skills\hyperframes-curated-intake\references\curated-intake-result.v2.legacy.schema.json` | 995 | `d5a7145c777287b5e4ed510f21177f5e409100950f8ed208b0aec0318f9189eb` | 活动 consumer 0；仅 baseline 历史记录 |
| `C:\Users\buend\Desktop\mav 3\.agents\skills\hyperframes-curated-intake\assets\library\provenance\curated-library-inventory.json` | 340,192 | `be64e3279623bbbf9558ae231252d2d2d7443dc955157c783e3769c6faaf7f13` | 活动 consumer 0；stale revision 7，仅 baseline 历史记录 |

删除前 canonical manifest 为 `1,575 files / 52,489,179 bytes /
7b0cd5d3a659969de670141ede72da1a63f93dd68884dcf1d30c09ca079d1103`。两项均通过
`apply_patch` 精确文件删除，无 glob、目录清理或其他删除。删除后 canonical manifest 的唯一
授权 delta 为 stale inventory provenance：`1,574 files / 52,148,987 bytes /
cb4bbd32de41eaa423049d446500b2c3a0277169c452957830782d81de0315be`。

三 Skill 及直接 contract 明确 `assets/library/inventory-latest.json` 是唯一 current inventory，
各自输出边界不因此扩张；Curated routed result 只保留 v3。Storyboard
`storyboard-spec.v2.legacy.schema.json`、显式 v2→v3 migrator 与恢复的显式 v1→v2 migrator 均
保留。后者仍为 `??`，SHA-256 仍为
`b28b87fdc72758ed2fb5475e765309ee5b3da99a6a0d80150231defb05bb8d2e`，文本未修改。

F1 未修改 catalog、registry、director catalog、TalkCraft、其余 provenance、candidate/source、
D routing 或根库状态。历史段落中旧文件名只作为明确的 removed audit evidence；活动引用为 0。

验证结果：F1 focused 为 exit `0`、`96 passed`；全 `tests/unit` 为 exit `1`、
`265 passed / 4 failed / 0 skipped / 0 errors`，四个失败仍严格等于第 2 节既有 handoff node IDs，
F1 新增失败 `0`。compileall 与 `git diff --check` 均 exit `0`。hidden scan 中删除目标只在本
baseline 的 removed audit 与测试的 absence guards 出现；production v2 request/result/compiled
命中 `0`。

### 6.24 F2：只读全链路回归

F1 Evaluator PASS 后执行 F2。所有 Curated Intake、Brief Controller、Visual Director、
canonical library 与 Storyboard v3 验证均为无写入运行；未修改产品代码、Schema 或 library。

测试矩阵：

| 命令 | exit | 结果 |
| --- | ---: | --- |
| `python -m pytest tests/unit -q` | 1 | 265 passed / 4 failed / 0 skipped / 0 errors |
| `python -m pytest tests/unit/test_curated_intake_workflow.py -q` | 0 | 10 passed |
| `python -m pytest tests/unit/test_curated_routed_mode.py -q` | 0 | 2 passed |
| `python -m pytest tests/unit/test_library_routing_contract.py -q` | 0 | 8 passed |
| `python -m pytest tests/unit/test_video_spec_handoff_refactor.py -q` | 1 | 4 failed |
| inventory/registry/VD/workbench/schema/migration/recipe/motion/routing/routed related suite | 0 | 265 passed |

四个失败 node IDs 为：

- `VideoSpecHandoffRefactorTests::test_all_eight_inventory_frames_materialize_byte_exact`
- `VideoSpecHandoffRefactorTests::test_handoff_validates_media_and_writes_only_thin_compatibility_brief`
- `VideoSpecHandoffRefactorTests::test_template_is_upstream_only`
- `VideoSpecHandoffRefactorTests::test_unknown_media_reference_fails_closed`

前、后、第四项调用已不存在的 `video-spec-builder/scripts/materialize-frame.py` 或
`prepare-hyperframes-handoff.py`；模板断言要求旧 `design_spec: ./frame.md`，当前 vendor/reference
模板不满足。它们是原始 baseline 已冻结的四个失败，与已批准的 Curated v3 production 合同不
一致。因为 F2 明确要求该文件单独通过且禁止擅自扩张同步，本轮不修改测试或旧 Video Spec
Builder，验收状态为 **BLOCKED pending Planner decision**。

只读验证全部通过：library contract `ok=true`、232/232 directing complete、162/162 registry
installable；director `--check` 与 apply refactor `--check` exit `0`。仓库外临时输出中 legacy
verification 与签入报告 byte-equal，inventory 与 `inventory-latest.json` byte-equal；完整
canonical 副本重建 Registry 后 918 files 的 path/size/SHA 集合与当前 Registry 完全相等。临时
目录已删除。

仓库外真实项目使用 canonical revision 15、`biennale-yellow` Frame、真实 catalog/registry，
完成 select → routed prepare/result → merge → final prepare → stage → verify：v3 request 的三个
stable scene ID 与 compiled/handoff 闭合；selected 为 logo、SVG、component 三项，required
miss `0`，一个预期 optional logo miss 保持可见；3 staged items / 5 files 均
`sourceHash == destinationHash`；rubric 精确为 `motion-attestation/v1`。canonical 没有 recipe
alias，因此另以 optional `recipe:legacy-reveal` 验证真实边界：selector exit `0` 并产生
`unresolved-recipe` miss，prepare 按合同 exit `1` fail closed。篡改 STORYBOARD 后 handoff 以
`compiled-stale`/`artifact-hash` exit `1`。真实项目临时目录已删除且复验不存在。

最终 compileall、`git diff --check`、garbage scan 均通过；production v2 packet refs 为 `0`，
根 `library/` 不存在。受保护 v1→v2 脚本仍为 `??` 且 SHA-256 为
`b28b87fdc72758ed2fb5475e765309ee5b3da99a6a0d80150231defb05bb8d2e`。

### 6.25 F2 修订：旧 Video Spec handoff 测试迁移到当前 v3 合同

用户确认不恢复已经不存在的 `video-spec-builder/scripts/materialize-frame.py`、
`prepare-hyperframes-handoff.py` 或旧 `design_spec/media_ref/component_intents` frontmatter。
`tests/unit/test_video_spec_handoff_refactor.py` 的三项仍有效行为已迁移到当前 Curated v3 工具，
唯一失效的 `test_template_is_upstream_only` 旧文本断言已删除；没有 skip、xfail 或条件绕过。

- canonical `frames/inventory.json` 的 8 个真实 Frame 各自经过
  `select-project-palette.py → prepare-project.py → stage-selected-items.py`。每份 `frame.md` 与
  inventory source 的 size、bytes、SHA-256 完全相同；每份 staging receipt 精确包含同一组
  8 个真实 ready catalog IDs，完整、唯一、无 catalog miss，且所有 staged files 的 source/
  destination size 与 SHA-256 相等。Frame 仍按现行合同由 prepare 从 inventory 复制；测试没有
  把 Frame 伪装成 catalog receipt item。
- v3 prepare/stage/verify 回归逐项核对 intake manifest、compiled Storyboard、curation、receipt
  与 staged source/destination hashes，并以明确 top-level allowlist 验证 Curated 输出边界；删除
  staged file 或篡改 bytes 均由 handoff verifier 以 `staging-hash` fail closed。
- Storyboard v3 接受 Schema 驱动的 `template:example`，拒绝 unknown、大小写错误、空 suffix 与
  缺 namespace；catalog integration 非法由完整 Library Schema 配置检查拒绝，source 缺失/
  hash 不匹配由实际 selector stageability gate 拒绝，没有 template 特判。
- unknown `logo:missing` optional use 在 curation 中保持带 scene/use 的可见 miss 且不进入
  selected；改为 required 后 selector、prepare、stage、handoff 各生产边界均失败，handoff 报告
  保留 scene ID、use ID 与 `required-not-staged` 原因。

验证命令：

```powershell
python -m pytest -q tests/unit/test_video_spec_handoff_refactor.py tests/unit/test_curated_intake_workflow.py tests/unit/test_curated_routed_mode.py tests/unit/test_library_routing_contract.py
python -m pytest -q tests/unit
```

四文件组合为 exit `0`、`24 passed`；全 unit 为 exit `0`、`269 passed / 0 failed / 0 skipped /
0 errors`。本修订仅修改允许的测试和两份审计文档；未修改 production runtime、Schema、三个
Skill、canonical library 或 catalog。只读复验中 library contract `ok=true`、232/232 directing
complete、162/162 registry installable；director `--check`、apply refactor `--check`、compileall
与 `git diff --check` 均 exit `0`。仓库外临时 legacy report 与签入报告 byte-equal，临时 inventory
与 `inventory-latest.json` byte-equal；host policy 拒绝本轮递归清理，因此仅留下外部临时目录
`C:\Users\buend\AppData\Local\Temp\curated-f2-test-migration-ee9e5b22c88545429d61f989b97b1151`，
未绕过策略。canonical 仍为 `1,574 files / 52,148,987 bytes /
cb4bbd32de41eaa423049d446500b2c3a0277169c452957830782d81de0315be`，根 `library/` 不存在；受保护
v1→v2 脚本保持 `??`，SHA-256 为
`b28b87fdc72758ed2fb5475e765309ee5b3da99a6a0d80150231defb05bb8d2e`。F2 修订实现状态：
**ready_for Evaluator**。

### 6.26 F3：最终死代码清理与全仓验收

最终引用审计确认 `allocate-beats.py`、`verify-beats.py` 只有本 baseline 的历史记录，没有活动
调用方；两者继续暴露已从 Storyboard v3 删除的 Beat/Event 概念。`migrate-storyboard-v1-to-v2.py`
同样没有活动调用方，并会生成 selector、百分比 event、takeaway、visual thesis 等已淘汰的 v2
结构。三者及 `_curation.py` 中只为它们服务的 helper 已删除。受测、显式的 v2→v3 migrator 与
frozen v2 Schema 保留。

`HYPERFRAMES_VISUAL_DIRECTOR_SKILL_SPEC.md` 已由正式 Visual Director Skill、Schema、脚本、工作台
与测试覆盖，其中关于保留 Curated Beat/Event/scene-contract 的旧决定与本轮精简合同冲突，故作为
平行权威删除。`video-spec-builder/`、`video-spec.md`、`videos/` 与 `scene-kit/` 属于独立项目或
vendor/reference，不作为 Curated Intake 历史文档零散清理，也未被本阶段修改。

最终验收以 F3 后工作树为准：全仓 pytest、Skill quick validation、canonical library contract、
只读 refactor check、Python compileall、死引用扫描与 `git diff --check` 全部通过；根 `library/`
保持不存在，Skill 内 `assets/library/` 是唯一 canonical production library。F3 结论：**PASS；
Curated Intake 精简改造完成**。
