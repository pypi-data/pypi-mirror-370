# ErisPulse-HelpModule
ErisPulse 帮助命令模块，提供自动化的命令帮助系统，支持查看所有可用命令及其用法说明

## 功能特性
提供 Event 子模块中 command 模块中统一的命令帮助功能
- 自动收集并显示所有已注册的命令
- 支持查看特定命令的详细帮助信息
- 支持命令分组显示
- 可配置是否显示隐藏命令
- 提供简洁和详细两种显示样式
- 支持命令别名显示

## 使用方法

### 基本命令

```
/help           # 显示所有可用命令的简要帮助
/help <命令名>   # 显示指定命令的详细帮助信息
```

### 命令别名

```
/h              # 等同于 /help
/帮助            # 等同于 /help
/命令帮助         # 等同于 /help
```

## 配置选项

模块支持以下配置选项，可以在 config.toml 中进行自定义：

```toml
[HelpModule]
show_hidden_commands = false  # 是否显示隐藏命令
style = "simple"              # 显示样式: "simple" 或 "detailed"
group_commands = true         # 是否按组显示命令
```

### 配置说明

- `show_hidden_commands`: 设置为 `true` 时，帮助命令会显示被标记为隐藏的命令
- `style`: 
  - `"simple"`: 简洁显示模式，只显示命令名称和简要描述
  - `"detailed"`: 详细显示模式，显示命令的更多详细信息
- `group_commands`: 设置为 `false` 时，不按组显示命令，所有命令将在同一列表中显示

## 依赖

- ErisPulse SDK 2.2.0+
