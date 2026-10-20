<div align="center">

# GitHub Project Publisher

![GitHub 项目发布助手：从本地代码到清晰、可安装的 GitHub 项目，涵盖 README 设计、隐私检查与发布验证。](docs/assets/hero-cover.png)

**让 Codex 把一个本地项目，整理成别人看得懂、装得上、能验证的 GitHub 仓库。**

[快速开始](#快速开始) · [工作流程](#工作流程) · [检查脚本](docs/checks.md) · [安全边界](SECURITY.md)

![Codex Skill](https://img.shields.io/badge/Codex-Skill-222222?style=flat-square)
![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square)
![Runtime standard library](https://img.shields.io/badge/运行依赖-Python_标准库-176B50?style=flat-square)
[![License: MIT](https://img.shields.io/badge/License-MIT-176B50?style=flat-square)](LICENSE)

</div>

> [!NOTE]
> 这是给 Codex 使用的工作流程与辅助脚本。发布需要你自己的 GitHub 授权；脚本可以独立运行，但不会自动替你发布。

一个面向项目作者的 Codex Skill：从发布前检查、README 设计、真实素材整理，到仓库发布与远端核对。也可以只改已有项目的介绍页，保留有用内容和原有工作。

在 Codex 中这样使用：

```text
使用 $publish-github-project 整理当前项目并发布到我的 GitHub。
保留“解决什么问题”和核心工作流；先检查隐私，再完善 README 和仓库简介。
```

当前技能包版本：**0.2.0**。本次新增项目结构选择、内容保留与素材版本检查，并同步首屏规范。[查看更新记录](CHANGELOG.md)

## 项目解决什么问题

代码能运行以后，发布仍有许多细节：怎样说明产品价值、哪些文件可以公开、没有截图怎么展示，以及上传后的内容是否与本地一致。

| 常见问题 | Skill 的处理方式 |
| --- | --- |
| README 改漂亮了，关键介绍却不见了 | 对照修改前后的内容，保留问题说明、角色分工和核心流程 |
| 不知道哪些文件会一起上传 | 检查候选文件，并在提交前审计完整暂存区的实际内容 |
| 没有截图或视频 | 条件允许时运行真实产品并用测试数据截图；没有视频就省略视频模块 |
| 有视频，但包含个人信息 | 检查画面、文件名、字幕与口播，完成必要处理后再展示 |
| 上传成功，却不知道页面是否可用 | 分别核对提交与文件、仓库元数据、CI 和实际页面显示 |
| 每个项目顺序不同，不知道是否漏了内容 | 按应用、工具、Skill 选择阅读顺序，记录保留内容和合理例外 |
| 已有 SVG 流程图却被当作缺图 | 检查实际引用，支持图片与 Mermaid；简单工具可说明理由后省略图表 |
| 替换视频时混入旧版或旧处理要求 | 按源文件哈希记录版本与处理决定，核对原片字节及旧引用 |

## 工作流程

<picture>
  <source media="(max-width: 640px)" srcset="docs/assets/workflow-mobile.svg">
  <img src="docs/assets/workflow.svg" alt="四步发布流程：检查范围与隐私，整理说明与真实素材，运行测试并审核提交内容，发布后核对文件和页面。">
</picture>

流程图直接使用仓库内的 SVG，文字与连线可编辑，展示不依赖 Mermaid 的交互组件。

**两种使用范围：** 新项目走完整发布流程；已有项目只更新 README、素材或元数据时，采用小范围更新，保留已经确认的内容。公开可见性、许可、合并和 Release 等决定遵循用户授权。

完整发布、较大 README 改版及视频替换会使用一份仓库外的本地发布方案：先记录基线与当前决定，再检查候选结果。普通文字或链接修正保持轻量，不强制重新设计页面。记录由 Codex 维护，无需使用者填写技术表单。

## 快速开始

### 1. 安装

在 Codex 中发送：

```text
使用 $skill-installer 安装这个仓库中的 skill：
https://github.com/ZhangShixing0/publish-github-project/tree/main/skills/publish-github-project
```

安装后确认技能列表中出现 `publish-github-project`；若未显示，重启 Codex 再检查。已有同名技能时，先对比和备份自己的修改，再更新。

技能目录中的 `VERSION` 标明版本；`package-manifest.json` 记录对应文件哈希。已有用户可按[版本检查与更新说明](docs/checks.md#技能版本与安装副本)检查文件是否完整、安装副本是否存在定制差异。

也可手动把本仓库的 `skills/publish-github-project` 文件夹放到目标项目的 `.agents/skills/` 下。安装整个技能文件夹，保留 `references/`、`scripts/`、`assets/` 与 `agents/`。[Codex 官方技能说明](https://learn.chatgpt.com/docs/build-skills)

### 2. 在目标项目里使用

**发布一个新项目**

```text
使用 $publish-github-project，把当前项目整理到我的 GitHub。
先检查文件与隐私，完善中文 README、工作流程和最短启动步骤。
```

**完善已有 README**

```text
使用 $publish-github-project 优化这个仓库的 README。
保留“解决什么问题”、角色职责和流程图；根据项目特点调整排版，
检查图片和链接，通过分支与草稿 PR 让我查看。
```

**补充介绍视频**

```text
使用 $publish-github-project，把我提供的视频合理展示到 README。
检查敏感信息，处理封面与播放入口，并验证 GitHub 页面效果。
```

### 3. 单独运行检查脚本

需要 **Python 3.10+ 和 Git**；检查脚本只使用 Python 标准库。发布及 GitHub API 核对还需要已经授权的 GitHub 工具；API 核对脚本使用 GitHub CLI `gh`。

在克隆后的本仓库根目录运行：

```bash
python skills/publish-github-project/scripts/audit_repository.py /path/to/your-project
python skills/publish-github-project/scripts/verify_project.py /path/to/your-project --strict
python skills/publish-github-project/scripts/verify_remote.py /path/to/your-project
```

替换示例路径；Windows 上带空格的路径请加引号。审计会输出类别与文件路径，不输出命中的敏感值。[完整参数与检查边界](docs/checks.md)

## 测试与验证

运行本仓库的回归测试、README 检查和发布文件审计：

```bash
python scripts/check.py
```

回归测试覆盖暂存区内容与工作区不一致、凭据识别、二进制人工复核、README 本地链接、响应式图片、首屏排列、SVG 安全约束，以及远端提交与文件哈希的核对。新版还覆盖内容保留、图表选择、素材替换和安装副本差异。测试不需要 GitHub 凭据，也不会创建远端仓库。

自动检查通过后，仍需核对功能描述、媒体隐私与实际页面。检查脚本的结果不能替代这些判断。

仓库附有 [GitHub Actions 配置模板](docs/ci-check.yml)，覆盖 Ubuntu / Windows 与 Python 3.10 / 3.12。**线上 CI 当前尚未启用**；启用方法见[检查脚本说明](docs/checks.md#启用-github-actions)。

<details>
<summary><strong>项目结构与维护方式</strong></summary>

```text
skills/publish-github-project/
├── SKILL.md             技能入口与决策流程
├── agents/openai.yaml   Codex 展示信息
├── references/          README、素材、发布与元数据指引
├── assets/              README 起始模板
├── scripts/             检查脚本、本地方案工具及回归测试
├── VERSION              技能包版本
└── package-manifest.json 对应版本的文件哈希
docs/                    脚本说明与工作流程图
scripts/check.py          仓库验证入口
```

仓库首页面向使用者；`skills/publish-github-project/` 是公开技能包的维护源，安装目录是它的使用副本。维护时先修改仓库、更新版本与清单并验证，再同步安装副本；有本地定制时先比较和保留。模板需要按项目证据改写，不应直接填满所有模块。

</details>

## 安全与许可

新仓库默认私有；已有项目默认通过分支和草稿 PR 更新。技能会遵循用户已有的授权，不把普通内容修改升级成无关操作。

凭据和隐私扫描属于启发式检查，不是完整安全审计。视频、音频、截图和客户文档仍需人工或额外工具复核。详见 [安全说明](SECURITY.md)。

采用 [MIT 许可证](LICENSE)，允许使用、修改和商用，须保留版权与许可说明。可安装的技能目录也包含许可证，便于分发时保留完整声明。

由 [ZhangShixing0](https://github.com/ZhangShixing0) 维护，来自实际项目发布与 README 改进过程。欢迎通过 [贡献说明](CONTRIBUTING.md) 提交可复现的问题与改进。
