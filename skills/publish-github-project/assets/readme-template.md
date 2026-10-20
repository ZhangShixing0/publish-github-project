<!-- Opening specification: references/readme-header.md in the publishing skill.
     Keep the following five blocks in order; close centering before the body.
     For requested language editions, insert a relative language-switch row
     immediately after the single H1; see references/readme-languages.md.
     Render the default badges with scripts/render_badges.py; retain the
     repository's badge manifest and accepted style during later updates. -->
<div align="center">

# {{PROJECT_NAME}}

{{HERO_WITH_DESCRIPTIVE_ALT}}

**{{ONE_SENTENCE_VALUE}}**

{{QUICK_NAVIGATION}}

{{VERIFIED_BADGES}}

</div>

> [!IMPORTANT]
> {{MATURITY_OR_SAFETY_NOTICE}}

{{OPTIONAL_VERSION_CENTER}}

## 项目解决什么问题

{{PROBLEM_AND_USER_OUTCOME}}

{{OPTIONAL_RESPONSIBILITY_TABLE}}

{{OPTIONAL_WORKFLOW_DIAGRAM}}

## 当前交付范围

| 组件 | 当前版本 | 责任 |
| --- | --- | --- |
| {{COMPONENT}} | {{VERSION}} | {{RESPONSIBILITY}} |

## 快速开始

### 环境要求

- {{VERIFIED_PREREQUISITE}}

### 安装与启动

```shell
{{VERIFIED_INSTALL_AND_START_COMMANDS}}
```

## 验证项目

```shell
{{VERIFIED_TEST_COMMAND}}
```

{{OPTIONAL_SYNTHETIC_EXAMPLE}}

<details>
<summary><strong>查看项目目录</strong></summary>

```text
{{RELEVANT_PROJECT_TREE}}
```

</details>

<details>
<summary><strong>查看数据与安全边界</strong></summary>

- {{IGNORED_SECRET_AND_RUNTIME_PATHS}}
- {{SYNTHETIC_DATA_RULE}}
- {{PRODUCTION_SECURITY_BOUNDARY}}

{{OPTIONAL_SECURITY_DOCUMENT_LINK}}

</details>

## 参与开发

{{CONTRIBUTION_AND_CHECK_COMMAND}}

## 许可与免责声明

{{LICENSE_AND_DOMAIN_DISCLAIMER}}
