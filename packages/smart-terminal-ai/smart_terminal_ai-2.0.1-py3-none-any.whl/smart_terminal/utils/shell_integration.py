"""
Shell integration utilities for different platforms
"""

import os
import platform
import subprocess
from pathlib import Path
from typing import List, Optional

class ShellIntegration:
    def __init__(self):
        self.os_type = platform.system().lower()
        self.is_windows = self.os_type == "windows"
        self.is_macos = self.os_type == "darwin"
        self.is_linux = self.os_type == "linux"
        
        # Get shell information first
        self.shell = self._detect_shell()
        
        # Platform-specific shell information
        self.shell_info = self._get_shell_info()
    
    def _detect_shell(self) -> str:
        """Detect the current shell"""
        if self.is_windows:
            return "powershell"
        else:
            return os.environ.get("SHELL", "bash").split("/")[-1]
    
    def _get_shell_info(self) -> dict:
        """Get information about the current shell"""
        if self.is_windows:
            return {
                "shell": "powershell",
                "profile_path": self._get_powershell_profile_path(),
                "profile_content": self._get_powershell_profile_content()
            }
        else:
            return {
                "shell": self.shell,
                "profile_path": self._get_unix_profile_path(),
                "profile_content": self._get_unix_profile_content()
            }
    
    def _get_powershell_profile_path(self) -> str:
        """Get PowerShell profile path"""
        try:
            result = subprocess.run(
                ["powershell", "-Command", "$PROFILE"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        # Fallback to default path
        return os.path.expanduser("~/Documents/WindowsPowerShell/Microsoft.PowerShell_profile.ps1")
    
    def _get_unix_profile_path(self) -> str:
        """Get Unix shell profile path"""
        if self.shell == "zsh":
            return os.path.expanduser("~/.zshrc")
        elif self.shell == "bash":
            return os.path.expanduser("~/.bashrc")
        elif self.shell == "fish":
            return os.path.expanduser("~/.config/fish/config.fish")
        else:
            return os.path.expanduser("~/.profile")
    
    def _get_powershell_profile_content(self) -> str:
        """Get PowerShell profile content for Smart Terminal"""
        return '''
# Smart Terminal Integration
function Smart-Terminal {
    python "$env:USERPROFILE\\smart-terminal\\src\\main.py" $args
}

Set-Alias -Name st -Value Smart-Terminal

Write-Host "Smart Terminal loaded. Use 'st' command." -ForegroundColor Green
'''
    
    def _get_unix_profile_content(self) -> str:
        """Get Unix shell profile content for Smart Terminal"""
        return '''
# Smart Terminal Integration
smart_terminal() {
    python3 "$HOME/smart-terminal/src/main.py" "$@"
}

alias st='smart_terminal'

echo "Smart Terminal loaded. Use 'st' command."
'''
    
    def install_shell_integration(self, install_path: str) -> bool:
        """Install shell integration for Smart Terminal"""
        try:
            profile_path = self.shell_info["profile_path"]
            
            # Create profile directory if it doesn't exist
            profile_dir = Path(profile_path).parent
            profile_dir.mkdir(parents=True, exist_ok=True)
            
            # Create profile file if it doesn't exist
            if not Path(profile_path).exists():
                Path(profile_path).touch()
            
            # Read existing profile content
            with open(profile_path, 'r') as f:
                existing_content = f.read()
            
            # Check if Smart Terminal is already installed
            if "Smart Terminal" in existing_content:
                return True  # Already installed
            
            # Add Smart Terminal integration
            integration_content = self.shell_info["profile_content"]
            
            # Update paths in integration content
            if self.is_windows:
                integration_content = integration_content.replace(
                    "$env:USERPROFILE\\smart-terminal\\src\\main.py",
                    f"{install_path}\\src\\main.py"
                )
            else:
                integration_content = integration_content.replace(
                    "$HOME/smart-terminal/src/main.py",
                    f"{install_path}/src/main.py"
                )
            
            # Append to profile
            with open(profile_path, 'a') as f:
                f.write(integration_content)
            
            return True
            
        except Exception as e:
            print(f"Failed to install shell integration: {e}")
            return False
    
    def uninstall_shell_integration(self) -> bool:
        """Uninstall shell integration"""
        try:
            profile_path = self.shell_info["profile_path"]
            
            if not Path(profile_path).exists():
                return True  # Nothing to uninstall
            
            # Read profile content
            with open(profile_path, 'r') as f:
                content = f.read()
            
            # Remove Smart Terminal integration
            lines = content.split('\n')
            filtered_lines = []
            skip_next = False
            
            for line in lines:
                if "# Smart Terminal Integration" in line:
                    skip_next = True
                    continue
                elif skip_next and line.strip() == "":
                    skip_next = False
                    continue
                elif skip_next:
                    continue
                else:
                    filtered_lines.append(line)
            
            # Write back filtered content
            with open(profile_path, 'w') as f:
                f.write('\n'.join(filtered_lines))
            
            return True
            
        except Exception as e:
            print(f"Failed to uninstall shell integration: {e}")
            return False
    
    def get_installation_instructions(self) -> str:
        """Get platform-specific installation instructions"""
        if self.is_windows:
            return """
Windows Installation:
1. Clone the repository to C:\\Users\\YourUsername\\smart-terminal
2. Run: python install_windows.ps1
3. Restart PowerShell
4. Use 'st' command
"""
        else:
            return """
macOS/Linux Installation:
1. Clone the repository to ~/smart-terminal
2. Run: chmod +x install_unix.sh && ./install_unix.sh
3. Restart terminal
4. Use 'st' command
"""
    
    def check_shell_integration(self) -> bool:
        """Check if shell integration is properly installed"""
        profile_path = self.shell_info["profile_path"]
        
        if not Path(profile_path).exists():
            return False
        
        try:
            with open(profile_path, 'r') as f:
                content = f.read()
                return "Smart Terminal" in content
        except:
            return False 