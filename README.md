# mav-mg

**中文** · [English](README.en.md) · [下载 Skill](https://github.com/maverickgao8848/mav-mg/archive/refs/heads/main.zip) · [观看 60 秒演示](https://github.com/maverickgao8848/mav-mg/raw/refs/heads/main/assets/showcase/hyperframes-curated-intake-demo-zh.mp4)

**用自然语言，把文章、脚本和想法变成有导演感的 MG 动画方案。** 先看图选风格，再一次审阅整条分镜；确认后交给 HyperFrames 制作。

[![观看 60 秒演示](assets/showcase/demo-contact-sheet.jpg)](https://github.com/maverickgao8848/mav-mg/raw/refs/heads/main/assets/showcase/hyperframes-curated-intake-demo-zh.mp4)

## 直接看图选 Frame

配色、字级、构图一起比较。复制图片下的风格名即可使用，点击图片可读完整规范。以下是风格示意，字体可能使用系统替代；不是成片截图。

<table>
<tr>
<td width="50%"><a href="assets/library/frames/biennale-yellow/FRAME.md"><img src="assets/showcase/frames/biennale-yellow.svg" alt="Biennale Yellow" width="480"></a><br><b>Biennale Yellow</b><br>策展 / 文化 / 思想<br><code>biennale-yellow</code></td>
<td width="50%"><a href="assets/library/frames/bmw-m-engineered-contrast/FRAME.md"><img src="assets/showcase/frames/bmw-m-engineered-contrast.svg" alt="BMW M Engineered Contrast" width="480"></a><br><b>BMW M Engineered Contrast</b><br>红蓝斜带 · 工程 / 硬件 / 性能<br><code>bmw-m-engineered-contrast</code></td>
</tr>
<tr>
<td width="50%"><a href="assets/library/frames/broadside/FRAME.md"><img src="assets/showcase/frames/broadside.svg" alt="Broadside" width="480"></a><br><b>Broadside</b><br>宣言 / 观点 / 强节奏发布<br><code>broadside</code></td>
<td width="50%"><a href="assets/library/frames/cartesian/FRAME.md"><img src="assets/showcase/frames/cartesian.svg" alt="Cartesian" width="480"></a><br><b>Cartesian</b><br>方法论 / 咨询 / 结构化解释<br><code>cartesian</code></td>
</tr>
<tr>
<td width="50%"><a href="assets/library/frames/cobalt-grid/FRAME.md"><img src="assets/showcase/frames/cobalt-grid.svg" alt="Cobalt Grid" width="480"></a><br><b>Cobalt Grid</b><br>研究 / 数据 / AI 与系统<br><code>cobalt-grid</code></td>
<td width="50%"><a href="assets/library/frames/dell-1996/FRAME.md"><img src="assets/showcase/frames/dell-1996.svg" alt="Dell 1996" width="480"></a><br><b>Dell 1996</b><br>复古科技 / 互联网文化 / 趣味产品<br><code>dell-1996</code></td>
</tr>
<tr>
<td width="50%"><a href="assets/library/frames/ferrari-editorial-chiaroscuro/FRAME.md"><img src="assets/showcase/frames/ferrari-editorial-chiaroscuro.svg" alt="Ferrari Editorial Chiaroscuro" width="480"></a><br><b>Ferrari Editorial Chiaroscuro</b><br>高端品牌 / 人物 / 编辑叙事<br><code>ferrari-editorial-chiaroscuro</code></td>
</tr>
</table>

## 开始使用

点击顶部「下载 Skill」并解压，将解压后的整个文件夹重命名为 `mav-mg`，再放到项目的 `.agents/skills/` 目录下。仓库根目录就是 Skill：`SKILL.md`、README、许可证、脚本、Schema 和素材都在包内。

需要 Python 3.11+。在这个 Skill 文件夹内运行：

```powershell
python -m pip install -r requirements.txt
```

在 Codex 中打开项目，粘贴材料并直接说：

```text
用 mav-mg 把这篇文章策划成 60 秒中文 MG 动画。
风格用 cobalt-grid，面向第一次了解这个主题的人。
先推荐需要动画的段落，和我一起确认整条 Storyboard，再交给 HyperFrames 制作。
```

已有风格选择和需求会直接沿用；只集中询问未确定的事项。你只需提供材料、看图选方向、确认整条分镜。Skill 负责绑定真实素材、记录来源和许可证并验证交接；后续构建与渲染需另装 HyperFrames 和 Node.js。

[Skill 入口](SKILL.md) · [来源与授权](assets/library/provenance/talkcraft-partner-authorization.md)

## 许可与商业授权

本仓库整体使用 [PolyForm Noncommercial License 1.0.0](LICENSE)。个人学习、研究、实验、爱好项目以及符合许可证定义的教育和其他非商业用途可以使用、修改和分发；**任何预期商业应用、为公司或客户制作内容、收费服务、商业产品集成或其他商业用途，都应先申请单独的商业授权。**

申请方式：在本仓库提交一个标题为 `Commercial License Request / 商业授权申请` 的 Issue，简要说明使用主体、使用场景、预计发布范围和联系方式。不要在公开 Issue 中填写敏感信息。

素材库中的第三方条目仍可能带有各自的来源与许可证元数据；使用或再分发前请同时检查对应条目。若摘要与 `LICENSE` 正文存在差异，以正文为准。
