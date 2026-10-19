# 三个检查脚本

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
```

检查标题、基础信息入口、本地链接、响应式图片引用、SVG 安全约束和发布资源路径。`--strict` 将结构警告视为失败；`--visual` 增加首屏视觉与图片检查。

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

## 验证这个 Skill 仓库

```bash
python scripts/check.py
```

该命令依次运行回归测试、严格 README 视觉结构检查、当前发布候选文件审计，不访问网络，也不执行 GitHub 发布。它使用 Python 标准库，不需要安装第三方 Python 包。

## 启用 GitHub Actions

仓库提供 [CI 模板](ci-check.yml)，尚未启用线上工作流。模板在 Ubuntu / Windows 上分别使用 Python 3.10 / 3.12 运行相同的本地检查，不要求额外的仓库 Secrets。

具备工作流写入权限后，将模板复制到 `.github/workflows/check.yml` 并提交到仓库。工作流会响应 push 和 pull request；首次运行结束后，查看 Actions 页的实际结果，再添加状态徽章。

本地验证不能替代尚未完成的 CI 运行，也不能据此宣称四种矩阵环境均已通过。
