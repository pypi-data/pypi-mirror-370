"""
*****************************************************************************************
*
*   ===================================================
*       CropDrop Bot (CB) Theme [eYRC 2025-26]
*   ===================================================
*
*  This script is intended to check the versions of the installed
*  software/libraries in Task 0 of CropDrop Bot (CB) Theme [eYRC 2025-26].
*
*  Filename:		evaluator.py
*  Created:			14/08/2025
*  Last Modified:	14/08/2025
*  Author:			e-Yantra Team
*  
*  This software is made available on an "AS IS WHERE IS BASIS".
*  Licensee/end user indemnifies and will keep e-Yantra indemnified from
*  any and all claim(s) that emanate from the use of the Software or
*  breach of the terms of this agreement.
*  
*  e-Yantra - An MHRD project under National Mission on Education using ICT (NMEICT)
*
*****************************************************************************************
"""

# ===== Standard imports =====
import os
import sys
import platform
import shutil
import subprocess
from pathlib import Path

# ===== Third-party imports =====
import distro
from rich.console import Console
from rich.prompt import Confirm
from eyantra_autoeval.utils.common import run_shell_command

# ===== Helper functions =====
def check_gcc_or_gplusplus():
    return shutil.which("gcc") is not None or shutil.which("g++") is not None

def check_python3_version():
    return sys.version_info.major >= 3

def find_file(filename, search_paths):
    """Search for a file in given paths recursively"""
    for base_path in search_paths:
        base_path = Path(base_path).expanduser()
        if base_path.exists():
            for root, dirs, files in os.walk(base_path):
                if filename in files:
                    return True
    return False

def check_coppeliasim():
    system_os = platform.system()
    exe_name = "coppeliaSim.exe" if system_os == "Windows" else "coppeliaSim.sh"

    # Check PATH
    if shutil.which(exe_name):
        return True

    # Search common locations
    common_paths = [
        Path.home(),
        "/opt",
        "/usr/local",
        Path.home() / "Workspace/Software"
    ]
    return find_file(exe_name, common_paths)

def check_stm32cubeide():
    system_os = platform.system()
    exe_name = "STM32CubeIDE.exe" if system_os == "Windows" else "stm32cubeide"

    if shutil.which(exe_name):
        return True

    common_paths = [
        Path.home(),
        "/opt",
        "/usr/local",
        Path.home() / "STMicroelectronics",
        Path.home() / "Workspace/Software"
    ]
    return find_file(exe_name, common_paths)


# ===== Main Evaluator =====
def evaluate():
    result = {}
    console = Console()
    result["generate"] = False

    # ===== OS Information =====
    with console.status("[bold green]Gathering system information..."):
        distribution = {
            "machine": platform.machine(),
            "version": distro.version(best=True),
            "name": distro.name(),
        }
        result["os_info"] = distribution
        result["os_type"] = platform.system()

    # ===== OS Compatibility Check =====
    self_os_declaration = True
    if (
        result["os_info"]["name"] != "Ubuntu"
        or "24.04" not in result["os_info"]["version"]
        or result["os_info"]["machine"] != "x86_64"
    ):
        console.print(
            f"""[yellow]You are using [bold blue]{result["os_info"]["name"]} {result["os_info"]["version"]} ({result["os_info"]["machine"]})[/bold blue].  
We officially support Ubuntu 24.04 on x86_64 (baremetal or WSL). You may continue, but e-Yantra will not help with OS-specific installation issues.[/yellow]"""
        )
        self_os_declaration = Confirm.ask(
            "Do you accept to take ownership of your setup and not seek OS-specific help from e-Yantra?"
        )
    elif result["os_info"]["name"] == "Ubuntu":
        uname = run_shell_command("uname -r").split("-")
        if uname[-1] == "Microsoft":
            console.print(f"""[yellow]You are using Ubuntu {result["os_info"]["version"]} in WSL[/yellow]""")
            result["wsl"] = True
        else:
            console.print(f"""[yellow]You are using standalone Ubuntu {result["os_info"]["version"]}[/yellow]""")
            result["wsl"] = False
    else:
        console.print(f"[red]Unsupported OS and not WSL. Cannot proceed.[/red]")
        result["generate"] = False

    result["self-os-declaration"] = self_os_declaration

    # ===== Installation Checks =====
    with console.status("[bold green]Checking required tools and software..."):
        result["gcc_or_g++_installed"] = check_gcc_or_gplusplus()
        result["python3_version_ok"] = check_python3_version()
        result["coppeliasim_installed"] = check_coppeliasim()
        result["stm32cubeide_installed"] = check_stm32cubeide()

    # ===== Summary =====
    console.print("\n[bold underline]Installation Check Results:[/bold underline]")
    for key, value in {
        "GCC or G++": result["gcc_or_g++_installed"],
        "Python 3 Version OK": result["python3_version_ok"],
        "CoppeliaSim Installed": result["coppeliasim_installed"],
        "STM32CubeIDE Installed": result["stm32cubeide_installed"],
    }.items():
        status = "[green]✓[/green]" if value else "[red]✗[/red]"
        console.print(f"{status} {key}")

    # ===== Final Verdict =====
    if all([
        result["gcc_or_g++_installed"],
        result["python3_version_ok"],
        result["coppeliasim_installed"],
        result["stm32cubeide_installed"],
        self_os_declaration
    ]):
        console.print("\n[bold green]✅ All checks passed. Task 0 Output is correct![/bold green]")
        result["generate"] = True
    else:
        console.print("\n[bold red]❌ Task 0 Output is incorrect! Please verify installations.[/bold red]")
        result["generate"] = False

    return result


# if __name__ == "__main__":
#     evaluate()

