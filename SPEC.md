# Canvas CLI 项目需求

## 项目目标

为 UC Irvine Canvas (`canvas.eee.uci.edu`) 构建一个命令行工具,通过官方 REST API 实现课程、文件、作业、成绩等的快速查询和本地同步,替代浏览器手动点击的低效操作。

## 技术栈

- **语言**:Python 3.11+
- **核心依赖**:
  - `canvasapi` — Canvas REST API 的官方 Python SDK
  - `typer` — CLI 框架(子命令 + 自动 `--help` + 类型校验)
  - `rich` — 终端表格、彩色输出、进度条
  - `httpx` — 文件下载(支持异步并发)
  - `python-dotenv` — token 配置管理
- **包管理**:`uv`(比 pip 快得多)
- **目标平台**:macOS(Mac Mini M4 主用),保持跨平台兼容

## 配置

首次运行 `canvas init` 引导用户:
1. 提示去 `https://canvas.eee.uci.edu/profile/settings` → New Access Token 生成 token
2. token 存到 `~/.config/canvas-cli/config.toml`(权限 600)
3. Canvas base URL 默认 `https://canvas.eee.uci.edu`,可配置(便于以后换学校)
4. 本地同步根目录默认 `~/CanvasSync`,可配置

## 核心命令

### 课程相关

```
canvas courses                       # 列出当前学期所有在修课程(默认过滤 active)
canvas courses --all                 # 包括往期课程
canvas courses --term "Spring 2026"  # 按学期筛选
```

输出:课程代码、全名、学期、course_id、教授名,rich 表格格式。

### 文件相关

```
canvas files <course>                       # 列课程所有文件(按 folder 树形显示)
canvas files <course> --flat                # 平铺列出
canvas files <course> --download            # 下载该课所有文件到本地同步目录
canvas files <course> --download <path>     # 下载到指定路径
```

`<course>` 支持模糊匹配:`chem3lc`、`physics7c`、`bio94`、course_id 都能识别。优先匹配课程代码缩写。

### 作业相关

```
canvas assignments                           # 所有课程的未来 14 天作业
canvas assignments --upcoming 7              # 自定义天数
canvas assignments <course>                  # 单课程所有作业
canvas assignments --overdue                 # 已过期未提交的
canvas assignments --submitted               # 已提交的
```

输出:课程、作业名、due 时间(显示距离现在多久)、分数权重、提交状态。

### 成绩相关

```
canvas grades                       # 当前所有课的总成绩
canvas grades <course>              # 某课程所有作业的成绩明细
canvas grades --what-if <course>    # 假设性计算:输入未来作业预期分,看总分变化
```

### 公告与通知

```
canvas announcements                # 所有课程最近公告(默认 7 天内)
canvas announcements <course>       # 特定课程
canvas inbox                        # Canvas 站内信未读
canvas inbox --all                  # 包括已读
```

### 全文搜索(本地索引)

```
canvas search "Fischer"             # 在已下载文件名 + 模块名 + 公告里搜索
canvas search "Fischer" --content   # 也搜文件内容(PDF/docx 提取文本)
canvas search "Fischer" -c chem3lc  # 限定课程
```

文件名搜索秒出;`--content` 模式建立本地 SQLite + FTS5 索引,首次较慢,后续增量更新。

### 同步(核心杀手命令)

```
canvas sync                         # 同步所有在修课的文件到 ~/CanvasSync/<课程代码>/
canvas sync <course>                # 单课程
canvas sync --dry-run               # 预览将下载/更新哪些文件
canvas sync --since 2026-04-01      # 只同步该日期后修改的文件
```

行为:
- 增量同步,用 Canvas API 返回的 `updated_at` 字段对比本地 mtime
- 保留 Canvas 的 folder 结构
- 并发下载(默认 5 路),带 rich 进度条
- 同步完写一份 `manifest.json` 记录文件 ID → 本地路径映射,方便后续命令定位

### 日历整合

```
canvas calendar                     # 所有作业 due 日期,文本日历视图
canvas calendar --ical              # 输出 .ics 文件,可导入系统日历
canvas calendar --ical --output ~/canvas.ics
```

### 模块导航

```
canvas modules <course>             # 列课程所有模块和模块项
canvas modules <course> --next      # 找出下一个未完成的模块项
```

## 架构要求

### 项目结构

```
canvas-cli/
├── pyproject.toml
├── README.md
├── canvas_cli/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py              # typer 入口,子命令注册
│   ├── config.py           # 配置文件读写
│   ├── client.py           # canvasapi 客户端封装(单例,带缓存)
│   ├── commands/
│   │   ├── courses.py
│   │   ├── files.py
│   │   ├── assignments.py
│   │   ├── grades.py
│   │   ├── announcements.py
│   │   ├── search.py
│   │   ├── sync.py
│   │   └── calendar.py
│   ├── matchers.py         # 课程模糊匹配逻辑
│   ├── formatters.py       # rich 表格输出统一格式
│   └── cache.py            # 短期 API 响应缓存(避免重复请求)
└── tests/
```

### 关键设计原则

1. **API 响应缓存**:课程列表、作业列表这类查询用 5 分钟内存缓存,避免每个命令都重新请求。`--no-cache` 强制刷新。
2. **错误处理**:token 过期、网络失败、429 限流要有清晰提示而非 traceback。429 自动指数退避重试。
3. **离线可用**:已 sync 的内容应支持在无网络时通过 `canvas search`、`canvas files <course> --local` 查询本地缓存。
4. **可脚本化**:所有命令支持 `--json` 输出原始 JSON,方便管道和后续处理(例如喂给 Claude 做总结)。
5. **隐私**:token 永远不进 log;debug 模式下 mask 显示前 8 位。

## 必须做对的细节

- **课程代码识别**:UCI 课程代码格式如 `CHEM M3LC`,Canvas 里可能显示为 `Chemistry M3LC` 或 `CHEMM3LC LEC A`。matcher 需归一化(去空格、大小写不敏感)后做 substring 匹配,无歧义直接用,有歧义列候选让用户选。
- **学期筛选**:Canvas API 的 `enrollment_term_id` 字段需要先调一次 accounts API 拿到 term 列表做映射。
- **大文件下载**:>50MB 的文件用流式下载,不要一次读进内存。
- **断点续传**:同步中断后再跑 `canvas sync` 应能跳过已完成的文件。

## 不要做的事

- 不要爬网页,所有数据通过官方 API
- 不要自动提交作业(只读 + 下载,写操作仅限"标记公告已读"这类无害动作)
- 不要在 token 配置之外做账号登录流程

## 交付物

1. 可工作的 Python 包,`uv pip install -e .` 后 `canvas` 命令全局可用
2. README 包含安装、token 获取步骤、所有命令示例
3. 至少 `courses`、`files`、`assignments`、`sync`、`search` 五个核心命令完整实现并测试通过
4. 用我的真实 Canvas token 跑通端到端流程(token 我会自己加到 `.env`)

## 开发顺序

1. 搭骨架:`config.py` + `client.py` + `canvas init`
2. 实现 `courses` 命令验证 token 和 API 连通
3. 实现 `files` 列表(不下载)
4. 实现 `sync`(核心价值)
5. 实现 `assignments` + `grades`
6. 实现 `search`(先文件名,再 `--content`)
7. 实现 `calendar` 和 `announcements`
8. 打磨:缓存、错误处理、`--json` 输出
