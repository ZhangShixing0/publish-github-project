# 检查脚本与发布方案

从本仓库根目录执行；将示例路径替换为目标 Git 仓库的实际路径。运行环境为 Python 3.10+、Git，GitHub API 模式额外需要已授权的 `gh`。

## 1. 发布文件审计

```bash
python skills/publish-github-project/scripts/audit_repository.py /path/to/project
python skills/publish-github-project/scripts/audit_repository.py /path/to/project --staged
python skills/publish-github-project/scripts/audit_repository.py /path/to/project --deny-file /private/path/blocked-markers.txt --json
```

默认检查已跟踪文件与未被忽略的未跟踪文件。显式使用 `--staged` 时，读取完整索引中将被提交的实际内容，不以工作区副本代替。

`--deny` 可以重复传入精确阻止词；含敏感内容的词表应放在仓库外。媒体和其他二进制材料会产生需要人工复核的提示；`--strict-binaries` 将此类提示视为错误。超过扫描上限的内容会明确提示，不代表已经检查完成。

返回码：0 表示没有错误，但仍可能有警告；1 表示发现错误；2 表示检查未能完成。输出不会展示命中的敏感值。

## 2. README 与展示资源

```bash
python skills/publish-github-project/scripts/verify_project.py /path/to/project --strict
python skills/publish-github-project/scripts/verify_project.py /path/to/project --strict --visual
python skills/publish-github-project/scripts/verify_project.py /path/to/project --strict --visual --readme README.en.md
```

检查标题、基础信息入口、本地链接、响应式图片引用、SVG 安全约束和发布资源路径。`--strict` 将结构警告视为失败；`--visual` 增加首屏视觉与图片检查。

`--readme` 选择仓库内的另一份 README，检查该文件及其相对链接；多语言版本分别运行。标题后的独立语言切换行不会改变正文导航与徽章的位置。翻译语义、双向切换及 GitHub 页面仍需人工复核。`--plan` 针对默认 README 的基线，与 `--readme` 分开执行。

徽章按项目清单复用固定样式：

```bash
python skills/publish-github-project/scripts/render_badges.py docs/badges/badges.json
python skills/publish-github-project/scripts/render_badges.py docs/badges/badges.json --check
```

前者生成清单中指定的 SVG；`--check` 只读比较，可发现缺失文件以及颜色、尺寸、文字等输出变化。清单中记录事实来源，但来源是否支持徽章内容仍需核对。本仓库的 `scripts/check.py` 同时检查两种 README 和这套徽章。

`--visual` 默认检查展示型首屏；工具可选 `--header-style compact`。保留已确认的特殊布局时使用 `--header-style preserve --header-note "实际保留理由"`，只跳过布局顺序检查，仍检查图片与 SVG。基础信息检查会寻找有内容的实际章节，导航或代码块中的关键词不算作章节。

这是结构检查。它不能证明原有重要内容都被保留，不能判断文案是否符合代码，也不能证明 GitHub 的实际渲染成功。文字完整性、图片可读性、浅色与深色显示仍需单独复核。

返回码：0 表示检查通过；1 表示检查发现错误或严格模式下的警告；2 表示检查未完成。

## 3. 远端提交与文件核对

普通 Git 发布后：

```bash
python skills/publish-github-project/scripts/verify_remote.py /path/to/project --branch main
```

目标提交需要已经存在于本地对象库中。默认比较本地 HEAD 与远端分支，并检查文件树；`--offline` 仅比较本地缓存的远端跟踪引用，不代表当前线上状态。

通过 API 创建提交，或 Git 传输不可用时：

```bash
python skills/publish-github-project/scripts/verify_remote.py /path/to/project --transport github-api --github-repo OWNER/REPO --branch main --expected-sha FULL_COMMIT_SHA --file-manifest /private/path/published-files.json --allow-dirty
```

替换大写示例值。`published-files.json` 是从仓库相对路径到完整 Git blob ID 的平面 JSON 对象；blob ID 不是普通文件的 SHA-256 值。`--allow-dirty` 仅允许从有未提交文件的目录执行，不会证明这些文件已经发布。

此脚本只核对分支提交、文件树及提供的 blob ID。仓库可见性、简介、主题、CI、媒体播放和页面显示必须分别核对。

返回码：0 表示核对通过；1 表示内容不一致或发现受阻文件；2 表示无法完成核对。

## 本地发布方案

在大幅改写 README 或替换素材前，记录原有内容与本次任务范围。方案和基线保存到目标仓库之外，避免发布本地素材路径或私有原文：

```bash
python skills/publish-github-project/scripts/publication_plan.py init /path/to/project --profile skill --scope readme --output /private/task/plan.json
python skills/publish-github-project/scripts/verify_project.py /path/to/project --strict --plan /private/task/plan.json
```

`--profile` 支持 `app`、`tool`、`skill`；`--scope` 支持 `initial`、`readme`、`media`。初始化生成待完成的方案，不能直接视为通过检查。代理根据实际项目补齐章节、图表和素材决定；不要求使用者填写 JSON。

方案检查包括基线哈希、H2 内容去向、未经复核的正文变化、章节顺序、SVG/图片或 Mermaid 引用、素材源与候选文件哈希、原片字节一致性以及旧文件/README 引用残留。小范围视频更新不会要求重新选择整页结构。详细字段见[发布方案规范](../skills/publish-github-project/references/publication-plan.md)。

它不能判断改写后的意思是否完整，也不能代替隐私与实际播放检查。退出码为 0（通过）、1（存在问题）、2（输入或文件无法检查）。

## 技能版本与安装副本

先验证克隆下来的技能包，再根据需要比较已有安装目录：

```bash
python skills/publish-github-project/scripts/skill_package.py verify
python skills/publish-github-project/scripts/skill_package.py verify --installed /path/to/installed/publish-github-project
```

检查 `VERSION`、文件清单和字节哈希，报告缺失、修改或额外文件；忽略 Python 缓存。命令只读，不会覆盖个人修改。旧版没有版本文件/清单时，应先备份并对照更新。完整安装应包含许可证、版本和清单。

维护者以仓库的 `skills/publish-github-project/` 为维护源。完成修改并更新 `VERSION` 与根目录更新记录后，重新生成清单，再运行完整检查：

```bash
python skills/publish-github-project/scripts/skill_package.py build-manifest
python scripts/check.py
```

清单验证保证文件与该清单一致，不等同于独立签名或来源认证。不要重新生成下载包的清单来掩盖缺失/变更；先确认差异来源。

## 验证这个 Skill 仓库

```bash
python scripts/check.py
```

该命令依次运行回归测试、严格 README 视觉结构检查、当前发布候选文件审计和技能包完整性检查，不访问网络，也不执行 GitHub 发布。它使用 Python 标准库，不需要安装第三方 Python 包。本仓库保留作者已确认的封面，首屏采用默认居中规范，正文保持左对齐，不使用布局豁免。

## 启用 GitHub Actions

仓库提供 [CI 模板](ci-check.yml)，尚未启用线上工作流。模板在 Ubuntu / Windows 上分别使用 Python 3.10 / 3.12 运行相同的本地检查，不要求额外的仓库 Secrets。

具备工作流写入权限后，将模板复制到 `.github/workflows/check.yml` 并提交到仓库。工作流会响应 push 和 pull request；首次运行结束后，查看 Actions 页的实际结果，再添加状态徽章。

本地验证不能替代尚未完成的 CI 运行，也不能据此宣称四种矩阵环境均已通过。
