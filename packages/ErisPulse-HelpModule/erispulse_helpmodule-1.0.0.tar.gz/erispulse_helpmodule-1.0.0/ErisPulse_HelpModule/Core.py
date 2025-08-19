from ErisPulse import sdk
from ErisPulse.Core.Event import command, message
from ErisPulse.Core import config
from typing import Dict, List, Optional

class HelpModule:
    def __init__(self):
        self.sdk = sdk
        self.logger = sdk.logger.get_child("HelpModule")
        self._register_commands()
        
    @staticmethod
    def should_eager_load():
        return True
    
    def _get_config(self):
        """获取模块配置，如果不存在则创建默认配置"""
        module_config = config.getConfig("HelpModule")
        if not module_config:
            default_config = {
                "show_hidden_commands": False,
                "style": "simple",
                "group_commands": True
            }
            config.setConfig("HelpModule", default_config)
            self.logger.warning("未找到HelpModule配置，已创建默认配置")
            return default_config
        return module_config
    
    def _get_command_prefix(self) -> str:
        event_config = config.getConfig("ErisPulse.event", {})
        command_config = event_config.get("command", {})
        return command_config.get("prefix", "/")
        
    def _register_commands(self):
        prefix = self._get_command_prefix()
        
        @command(
            "help", 
            aliases=["h", "帮助", "命令帮助"], 
            help="显示帮助信息",
            usage="help [命令名] - 显示所有命令或指定命令的详细信息"
        )
        async def help_command(event):
            await self._handle_help_command(event)

    async def _handle_help_command(self, event: Dict) -> None:
        try:
            platform = event["platform"]
            if event.get("detail_type") == "group":
                target_type = "group"
                target_id = event["group_id"]
            else:
                target_type = "user"
                target_id = event["user_id"]
                
            # 获取命令参数
            args = event.get("command", {}).get("args", [])
            
            # 获取适配器实例
            adapter = getattr(sdk.adapter, platform)
            
            if args:
                # 查看特定命令的详细帮助
                cmd_name = args[0].lower()
                help_text = self._get_command_detail(cmd_name)
            else:
                # 显示所有命令的简要帮助
                # 根据配置决定是否显示隐藏命令
                module_config = self._get_config()
                show_hidden = module_config.get("show_hidden_commands", False)
                
                if show_hidden:
                    # 显示所有命令（包括隐藏命令）
                    commands_info = {}
                    all_commands = command.get_commands()
                    for cmd_name in all_commands:
                        # 只获取主命令，避免重复显示别名
                        cmd_info = command.get_command(cmd_name)
                        if cmd_info and cmd_name == cmd_info.get("main_name"):
                            commands_info[cmd_name] = cmd_info
                else:
                    # 只显示可见命令
                    commands_info = {}
                    visible_commands = command.get_visible_commands()
                    for cmd_name in visible_commands:
                        cmd_info = command.get_command(cmd_name)
                        if cmd_info:
                            commands_info[cmd_name] = cmd_info
                            
                help_text = self._format_help_text(commands_info, show_hidden)
            
            # 发送帮助信息
            await adapter.Send.To(target_type, target_id).Text(help_text)
        except Exception as e:
            self.logger.error(f"处理帮助命令时出错: {e}")
            if 'adapter' in locals():
                error_msg = "处理帮助命令时发生错误，请稍后再试"
                await adapter.Send.To(target_type, target_id).Text(error_msg)

    def _format_help_text(self, commands_info: Dict[str, Dict], show_hidden: bool = False) -> str:
        prefix = self._get_command_prefix()
        module_config = self._get_config()
        style = module_config.get("style", "simple")
        
        if style == "detailed":
            return self._format_detailed_help_text(commands_info, show_hidden)
        else:
            return self._format_simple_help_text(commands_info, show_hidden)
    
    def _format_simple_help_text(self, commands_info: Dict[str, Dict], show_hidden: bool = False) -> str:
        prefix = self._get_command_prefix()
        module_config = self._get_config()
        
        help_lines = [
            "=" * 50,
            "命令帮助",
            "=" * 50,
        ]
        
        if show_hidden:
            help_lines.append("[注意] 当前显示所有命令（包括隐藏命令）")
        
        help_lines.append(f"使用 '{prefix}help <命令名>' 查看具体命令的详细用法")
        help_lines.append("")
        
        # 根据配置决定是否按组显示命令
        if module_config.get("group_commands", True):
            # 按命令组分组
            grouped_commands = self._group_commands_by_category(commands_info)
            
            # 添加默认组的命令
            if "default" in grouped_commands:
                help_lines.append("[通用命令]")
                for cmd_name, cmd_info in grouped_commands["default"]:
                    help_lines.append(self._format_command_brief(cmd_name, cmd_info, prefix))
                help_lines.append("")
            
            # 添加其他组的命令
            for group, cmds in grouped_commands.items():
                if group == "default":
                    continue
                # 安全处理组名
                group_name = str(group) if group else "其他"
                help_lines.append(f"[{group_name}命令]")
                for cmd_name, cmd_info in cmds:
                    help_lines.append(self._format_command_brief(cmd_name, cmd_info, prefix))
                help_lines.append("")
        else:
            # 不分组显示所有命令
            help_lines.append("[所有命令]")
            for cmd_name, cmd_info in commands_info.items():
                help_lines.append(self._format_command_brief(cmd_name, cmd_info, prefix))
            help_lines.append("")
        
        # 添加页脚信息
        help_lines.append("-" * 50)
        help_lines.append(f"共 {len(commands_info)} 个可用命令")
        help_lines.append("=" * 50)
        
        return "\n".join(help_lines)
    
    def _format_detailed_help_text(self, commands_info: Dict[str, Dict], show_hidden: bool = False) -> str:
        prefix = self._get_command_prefix()
        module_config = self._get_config()
        
        help_lines = [
            "=" * 50,
            "命令帮助",
            "=" * 50,
        ]
        
        if show_hidden:
            help_lines.append("[注意] 当前显示所有命令（包括隐藏命令）")
        
        help_lines.append(f"使用 '{prefix}help <命令名>' 查看具体命令的详细用法")
        help_lines.append("")
        
        # 根据配置决定是否按组显示命令
        if module_config.get("group_commands", True):
            # 按命令组分组
            grouped_commands = self._group_commands_by_category(commands_info)
            
            # 添加默认组的命令
            if "default" in grouped_commands:
                help_lines.append("[通用命令]")
                for cmd_name, cmd_info in grouped_commands["default"]:
                    help_lines.append(self._format_command_detailed(cmd_name, cmd_info, prefix))
                help_lines.append("")
            
            # 添加其他组的命令
            for group, cmds in grouped_commands.items():
                if group == "default":
                    continue
                # 安全处理组名
                group_name = str(group) if group else "其他"
                help_lines.append(f"[{group_name}命令]")
                for cmd_name, cmd_info in cmds:
                    help_lines.append(self._format_command_detailed(cmd_name, cmd_info, prefix))
                help_lines.append("")
        else:
            # 不分组显示所有命令
            help_lines.append("[所有命令]")
            for cmd_name, cmd_info in commands_info.items():
                help_lines.append(self._format_command_detailed(cmd_name, cmd_info, prefix))
            help_lines.append("")
        
        # 添加页脚信息
        help_lines.append("-" * 50)
        help_lines.append(f"共 {len(commands_info)} 个可用命令")
        help_lines.append("=" * 50)
        
        return "\n".join(help_lines)
    
    def _group_commands_by_category(self, commands_info: Dict[str, Dict]) -> Dict[str, List]:
        grouped_commands = {}
        for cmd_name, cmd_info in commands_info.items():
            group = cmd_info.get("group")
            group = "default" if group is None else group
            if group not in grouped_commands:
                grouped_commands[group] = []
            grouped_commands[group].append((cmd_name, cmd_info))
        return grouped_commands
    
    def _format_command_brief(self, cmd_name: str, cmd_info: Dict, prefix: str) -> str:
        # 主命令名
        formatted = f"  {prefix}{cmd_name}"
        
        # 帮助文本
        help_text = cmd_info.get("help", "暂无描述")
        formatted += f" - {help_text}"
        
        return formatted
    
    def _format_command_detailed(self, cmd_name: str, cmd_info: Dict, prefix: str) -> str:
        # 主命令名
        formatted = f"  {prefix}{cmd_name}"
        
        # 帮助文本
        help_text = cmd_info.get("help", "暂无描述")
        formatted += f"\n    描述: {help_text}"
        
        # 别名信息
        aliases = []
        for alias, main_name in command.aliases.items():
            if main_name == cmd_info['main_name'] and alias != cmd_info['main_name']:
                aliases.append(alias)
        
        if aliases:
            formatted += f"\n    别名: {', '.join(f'{prefix}{a}' for a in aliases)}"
        
        # 使用示例
        if cmd_info.get("usage"):
            usage = cmd_info['usage'].replace("/", prefix)
            formatted += f"\n    用法: {usage}"
            
        # 权限信息
        if cmd_info.get("permission"):
            formatted += f"\n    权限: 需要特殊权限"
            
        # 隐藏状态
        if cmd_info.get("hidden"):
            formatted += f"\n    状态: 隐藏命令"
        
        return formatted
    
    def _get_command_detail(self, cmd_name: str) -> str:
        prefix = self._get_command_prefix()
        
        # 查找命令(支持别名) 使用安全访问方式
        cmd_info = command.get_command(cmd_name)
        
        if not cmd_info:
            return f"错误: 未找到命令 '{cmd_name}'"
        
        # 构建详细帮助
        lines = [
            "=" * 50,
            f"命令详情: {prefix}{cmd_info['main_name']}",
            "=" * 50,
            f"描述: {cmd_info.get('help', '暂无描述')}"
        ]
        
        # 别名信息
        aliases = []
        for alias, main_name in command.aliases.items():
            if main_name == cmd_info['main_name'] and alias != cmd_info['main_name']:
                aliases.append(alias)
        
        if aliases:
            lines.append(f"别名: {', '.join(f'{prefix}{a}' for a in aliases)}")
        
        # 使用示例
        if cmd_info.get("usage"):
            lines.append("")
            lines.append("使用示例:")
            usage = cmd_info['usage'].replace("/", prefix)
            lines.append(f"  {usage}")
        
        # 权限信息
        if cmd_info.get("permission"):
            lines.append("")
            lines.append("权限: 需要特殊权限才能使用此命令")
        
        # 隐藏状态
        if cmd_info.get("hidden"):
            lines.append("")
            lines.append("注意: 这是一个隐藏命令，不会在常规帮助中显示")
            
        # 显示命令组信息
        if cmd_info.get("group"):
            lines.append("")
            lines.append(f"分组: {cmd_info['group']}")
        
        lines.append("=" * 50)
        return "\n".join(lines)