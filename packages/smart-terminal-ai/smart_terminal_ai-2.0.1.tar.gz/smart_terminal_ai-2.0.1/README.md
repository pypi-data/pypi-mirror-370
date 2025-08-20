# Smart Terminal 🚀 v2.0

AI-powered terminal assistant that converts natural language to shell commands. Works seamlessly on Windows, macOS, and Linux with enhanced features and capabilities.

## ✨ Enhanced Features

### **Core Features**
- **Natural Language Processing**: Just type what you want to do in plain English
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Smart Learning**: Learns from your command history to provide better suggestions
- **Safe Execution**: Prevents dangerous commands from running
- **Interactive Mode**: Chat with your terminal naturally
- **AI-Powered Suggestions**: Get intelligent command recommendations

### **🆕 New in v2.0**
- **Git Integration**: Full git workflow support with natural language
- **System Monitoring**: Check processes, memory, disk usage, and more
- **Network Operations**: Ping, download, and network diagnostics
- **Text Processing**: Advanced text manipulation and search
- **Command Bookmarks**: Save and reuse frequently used commands
- **Command History**: Track and replay previous commands
- **Workflow Suggestions**: Get next-step recommendations
- **Enhanced Safety**: Multiple safety levels and confirmations
- **Plugin System**: Extensible architecture for custom commands
- **Smart Completions**: Context-aware command completions

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI (recommended)
pip install smart-terminal-ai

# Or install from source
git clone https://github.com/yourusername/smart-terminal.git
cd smart-terminal
pip install -e .
```

### Usage

```bash
# Interactive mode
smart-terminal

# Direct command
smart-terminal "make a folder called my_project"

# Short alias
st "create a backup of my documents"
```

## 📖 Command Examples

### **File Operations**
| What you type | What it executes |
|---------------|------------------|
| "make a folder called random" | `mkdir random` |
| "delete the old backup folder" | `rm -rf backup/` |
| "show all hidden files" | `ls -la` |
| "copy file.txt to documents" | `cp file.txt documents/` |
| "compress my project folder" | `tar -czf project.tar.gz project/` |

### **Git Operations**
| What you type | What it executes |
|---------------|------------------|
| "git init new repository" | `git init` |
| "add all files to git" | `git add .` |
| "commit with message fix bug" | `git commit -m 'fix bug'` |
| "push to main branch" | `git push origin main` |
| "clone repository from url" | `git clone <url>` |

### **System Operations**
| What you type | What it executes |
|---------------|------------------|
| "show running processes" | `ps aux` (Unix) / `Get-Process` (Windows) |
| "check disk usage" | `df -h` (Unix) / `Get-WmiObject Win32_LogicalDisk` (Windows) |
| "show memory usage" | `free -h` (Unix) / `Get-WmiObject Win32_ComputerSystem` (Windows) |
| "system uptime" | `uptime` (Unix) / `Get-Uptime` (Windows) |

### **Network Operations**
| What you type | What it executes |
|---------------|------------------|
| "ping google.com" | `ping -c 4 google.com` |
| "download file from url" | `curl -o file url` |
| "show network ports" | `netstat -tuln` |
| "show ip address" | `ifconfig` / `ipconfig` |

### **Text Processing**
| What you type | What it executes |
|---------------|------------------|
| "edit file.txt" | `nano file.txt` / `notepad file.txt` |
| "search for pattern in files" | `grep -r pattern .` |
| "count lines in file.txt" | `wc -l file.txt` |
| "show first 10 lines of file" | `head -n 10 file` |

## 🖥️ Platform Support

- **Windows**: PowerShell commands with native Windows tools
- **macOS**: Unix commands optimized for macOS
- **Linux**: Full Linux command support

## 🧠 AI Features

### **Smart Learning**
- Remembers your command patterns and preferences
- Suggests commands based on usage history
- Learns from successful executions
- Adapts to your workflow over time

### **Context-Aware Suggestions**
- **Git Operations**: Complete git workflows and best practices
- **Python Development**: Virtual environments, package management
- **Node.js Workflows**: npm commands and project management
- **Docker Operations**: Container management and deployment
- **System Administration**: Process management, monitoring
- **Network Operations**: Connectivity testing, file downloads

### **Workflow Intelligence**
- Suggests logical next steps after commands
- Provides complete workflow guidance
- Learns common command sequences
- Offers alternatives for failed commands

### **Enhanced Safety Features**
- **Multiple Safety Levels**: Low, Medium, High protection
- **Dangerous Command Detection**: Prevents system damage
- **Confirmation Prompts**: For destructive operations
- **Sandbox Mode**: Test commands without execution
- **Backup Suggestions**: Automatic backup recommendations

## 📦 Requirements

- Python 3.8+
- Rich terminal support
- Git (optional, for git features)
- Internet connection (for AI features and downloads)

## 🔧 Advanced Configuration

Smart Terminal creates a configuration file at `~/.smart_terminal/config.json` with extensive customization options:

### **General Settings**
```json
{
  "general": {
    "confirm_dangerous_commands": true,
    "show_suggestions": true,
    "max_suggestions": 5,
    "suggest_bookmarks": true,
    "command_timeout": 30
  }
}
```

### **AI Settings**
```json
{
  "ai": {
    "enable_learning": true,
    "suggestion_threshold": 0.5,
    "max_history_size": 1000,
    "enable_context_suggestions": true
  }
}
```

### **Safety Settings**
```json
{
  "safety": {
    "check_dangerous_patterns": true,
    "require_confirmation_for_deletion": true,
    "sandbox_mode": false,
    "backup_before_delete": false
  }
}
```

## 🚀 Advanced Usage

### **Interactive Mode Commands**
```bash
st
# Then type naturally:
# "help" - Show comprehensive help
# "stats" - View detailed usage statistics
# "config" - Show current configuration
# "history" - View command history
# "bookmark <name> <command>" - Save command
# "clear" - Clear screen
# "version" - Show version information
# "install" - Install shell integration
```

### **Bookmarks and Aliases**
```bash
# Save frequently used commands
bookmark deploy "git add . && git commit -m 'Deploy' && git push"
bookmark backup "tar -czf backup-$(date +%Y%m%d).tar.gz ."

# Use bookmarks
st deploy
st backup
```

### **Command History**
```bash
# View recent commands
history

# Repeat commands from history
!5  # Repeat 5th command from history
```

### **Shell Integration**
Install shell integration to use `st` command directly:

```bash
# In interactive mode, type:
install

# Or manually add to your shell profile
# For zsh/bash: ~/.zshrc or ~/.bashrc
# For PowerShell: PowerShell profile
```

## 🛠️ Development

### **Setup Development Environment**
```bash
git clone https://github.com/yourusername/smart-terminal.git
cd smart-terminal
pip install -e ".[dev]"
```

### **Run Tests**
```bash
pytest
pytest src/smart_terminal/tests/test_enhanced_features.py
```

### **Code Formatting**
```bash
black src/
flake8 src/
```

### **Plugin Development**
Create custom plugins by extending the command mapper and builder:

```python
# Example plugin structure
class CustomPlugin:
    def __init__(self):
        self.commands = {
            "custom_action": self.handle_custom_command
        }
    
    def handle_custom_command(self, intent):
        return "custom command result"
```

## 📊 Enhanced Statistics

Track your usage with comprehensive analytics:
- **Total Commands Executed**: All-time command count
- **Success Rate**: Percentage of successful executions
- **Most Used Patterns**: Your favorite command types
- **Platform Usage**: Cross-platform usage statistics
- **Session History**: Current session command tracking
- **Learning Progress**: AI improvement metrics
- **Bookmark Usage**: Most used saved commands

## 🎯 Use Cases

### **Developers**
- Git workflow automation
- Project setup and management
- Code deployment processes
- Development environment setup

### **System Administrators**
- System monitoring and diagnostics
- Process management
- Network troubleshooting
- Automated maintenance tasks

### **Data Scientists**
- File processing and manipulation
- Environment management
- Data pipeline operations
- Analysis workflow automation

### **DevOps Engineers**
- Container management
- Deployment automation
- Infrastructure monitoring
- CI/CD pipeline management

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md).

### **Development Roadmap**
- [x] Enhanced NLP with context awareness
- [x] Git integration and workflows
- [x] System monitoring capabilities
- [x] Network operations support
- [x] Command bookmarking system
- [ ] Plugin marketplace
- [ ] Web interface for configuration
- [ ] Team collaboration features
- [ ] Integration with popular IDEs
- [ ] Voice command support
- [ ] Machine learning model improvements

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- Powered by [Click](https://click.palletsprojects.com/) for CLI framework
- Enhanced with [GitPython](https://gitpython.readthedocs.io/) for git integration
- System monitoring via [psutil](https://psutil.readthedocs.io/)
- Inspired by modern AI-powered developer tools

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/smart-terminal/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/smart-terminal/discussions)
- **Documentation**: [Project Wiki](https://github.com/yourusername/smart-terminal/wiki)

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/smart-terminal&type=Date)](https://star-history.com/#yourusername/smart-terminal&Date)

---

**Smart Terminal v2.0 - Making terminal interactions intelligent, intuitive, and powerful.** 🚀

**Made with ❤️ for developers who want to work smarter, not harder.**