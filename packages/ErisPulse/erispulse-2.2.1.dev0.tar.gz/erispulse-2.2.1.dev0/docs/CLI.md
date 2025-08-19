# ErisPulse 官方 CLI 命令手册

## 命令概述

ErisPulse CLI 提供以下命令组：

## 命令参考

### 包管理命令

| 命令       | 参数                      | 描述                                  | 示例                          |
|------------|---------------------------|---------------------------------------|-------------------------------|
| `install`  | `<package>... [--upgrade/-U] [--pre]` | 安装模块/适配器包（支持多个包）      | `epsdk install Yunhu Weather`  |
|            |                           | 支持远程包简称自动解析                | `epsdk install Yunhu -U` |
| `uninstall`| `<package>...`            | 卸载模块/适配器包（支持多个包）       | `epsdk uninstall old-module1 old-module2`  |
| `upgrade`  | `[package]... [--force/-f] [--pre]` | 升级指定模块/适配器或所有包         | `epsdk upgrade --force`       |
| `search`   | `<query> [--installed/-i] [--remote/-r]` | 搜索模块/适配器包             | `epsdk search github`         |
| `self-update` | `[version] [--pre] [--force/-f]` | 更新ErisPulse SDK本身           | `epsdk self-update`           |

### 模块管理命令

| 命令       | 参数       | 描述                  | 示例                  |
|------------|------------|-----------------------|-----------------------|
| `enable`   | `<module>` | 启用已安装的模块      | `epsdk enable chat`   |
| `disable`  | `<module>` | 禁用已安装的模块      | `epsdk disable stats` |

### 信息查询命令

| 命令          | 参数                      | 描述                                  | 示例                          |
|---------------|---------------------------|---------------------------------------|-------------------------------|
| `list`        | `[--type/-t <type>]`      | 列出已安装的模块/适配器               | `epsdk list --type=modules`   |
|               | `[--outdated/-o]`         | 仅显示可升级的包                      | `epsdk list -o`               |
|               |                           | `--type`: `modules`/`adapters`/`cli`/`all`  | `epsdk list -t adapters`      |
| `list-remote` | `[--type/-t <type>]`      | 列出远程可用的模块和适配器            | `epsdk list-remote`           |
|               | `[--refresh/-r]`          | 强制刷新远程包列表                    | `epsdk list-remote -r`        |
|               |                           | `--type`: `modules`/`adapters`/`cli`/`all`  | `epsdk list-remote -t all`    |

### 运行控制命令

| 命令       | 参数                      | 描述                                  | 示例                          |
|------------|---------------------------|---------------------------------------|-------------------------------|
| `run`      | `<script> [--reload] [--no-reload]` | 运行指定脚本                    | `epsdk run main.py`           |
|            |                           | `--reload`: 启用热重载模式            | `epsdk run app.py --reload`   |

## 高级用法

### 安装远程模块
CLI会自动检查远程仓库中的模块简称：
```bash
# 安装单个远程模块("Yunhu" 是远程适配器 "ErisPulse-YunhuAdapter" 的简称)
epsdk install Yunhu

# 安装多个远程模块
epsdk install Yunhu Weather GitHubParser

# 升级安装远程模块
epsdk install Yunhu --upgrade

# 安装预发布版本
epsdk install SomeModule --pre
```

### 卸载模块
```bash
# 卸载单个模块
epsdk uninstall SomeModule

# 卸载多个模块
epsdk uninstall Module1 Module2 Module3
```

### 批量升级
```bash
# 升级所有模块(需要确认)
epsdk upgrade

# 强制升级所有模块(跳过确认)
epsdk upgrade --force

# 升级指定模块
epsdk upgrade Module1 Module2

# 升级到预发布版本
epsdk upgrade SomeModule --pre
```

### 搜索模块
```bash
# 搜索所有模块
epsdk search keyword

# 仅搜索已安装的模块
epsdk search keyword --installed

# 仅搜索远程模块
epsdk search keyword --remote
```

### 自更新SDK
```bash
# 交互式更新到最新稳定版
epsdk self-update

# 更新到指定版本
epsdk self-update 2.1.14

# 包含预发布版本的更新
epsdk self-update --pre

# 强制更新到指定版本（即使版本相同）
epsdk self-update 2.1.14 --force
```

### 开发模式运行
使用热重载运行脚本，自动检测文件变化:
```bash
# 运行脚本（默认监控配置文件）
epsdk run dev.py

# 启用热重载模式（监控所有.py文件）
epsdk run dev.py --reload

# 禁用所有监控
epsdk run dev.py --no-reload
```

### 模块管理
```bash
# 启用模块
epsdk enable chat-module

# 禁用模块
epsdk disable old-module
```

## 技术细节

- 优先使用 `uv` 进行包管理 (如果已安装)
- 支持多源远程仓库查询
- 热重载模式支持:
  - 开发模式: 监控所有 `.py` 文件变化
  - 普通模式: 仅监控 `config.toml` 变更
- 自动检查模块的最低SDK版本要求
- 支持通过简称安装/卸载远程包

## 反馈与支持

如遇到 CLI 使用问题，请在 GitHub Issues 提交反馈。
