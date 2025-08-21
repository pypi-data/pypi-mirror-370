#!/usr/bin/env python3
"""
ZerisFetch - System information display tool
A neofetch-like tool for displaying system information with ASCII art
"""

import subprocess
import os
import sys

def run_bash_command(command):
    """Выполняет bash команду и возвращает результат"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except:
        return "N/A"

def get_info():
    """Получает системную информацию"""
    info = {}
    info['user'] = run_bash_command('whoami')
    info['host'] = run_bash_command('hostname')
    info['os'] = run_bash_command('cat /etc/os-release | grep "PRETTY_NAME" | cut -d\'"\' -f2 | cut -c1-25')
    info['kernel'] = run_bash_command('uname -r | cut -c1-20')
    info['uptime'] = run_bash_command('uptime -p | sed \'s/up //\' | cut -c1-20')
    info['shell'] = run_bash_command('basename "$SHELL"')
    info['cpu'] = run_bash_command('cat /proc/cpuinfo | grep "model name" | head -n1 | cut -d: -f2 | sed \'s/^ *//\' | cut -c1-30')
    info['memory'] = run_bash_command('free -h | awk \'/^Mem:/ {print $3"/"$2}\'')
    info['disk'] = run_bash_command('df -h / | awk \'NR==2 {print $3"/"$2}\'')
    return info

def get_distro():
    """Определяет дистрибутив"""
    os_release = run_bash_command('cat /etc/os-release')
    if 'ubuntu' in os_release.lower():
        return 'ubuntu'
    elif 'debian' in os_release.lower():
        return 'debian'
    elif 'arch' in os_release.lower():
        return 'arch'
    else:
        return 'linux'

def get_ascii_art(distro):
    """Возвращает ASCII арт для дистрибутива"""
    arts = {
        'debian': [
            "       _,met$$$$$gg.            ",
            "    ,g$$$$$$$$$$$$$$$P.         ",
            "  ,g$$P\"     \"\"\"Y$$.\"           ",
            " ,$$P'              `$$$.       ",
            "',$$P       ,ggs.     `$$b:     ",
            "`d$$'     ,$P\"'   .    $$$      ",
            " $$P      d$'     ,    $$P      ",
            " $$:      $$.   -    ,d$$'      ",
            " $$;      Y$b._   _,d$P'        ",
            " Y$$.    `.`\"Y$$$$P\"'           ",
            " `$$b      \"-.__                ",
            "  `Y$$                          "
        ],
        'ubuntu': [
            "         _                      ",
            "     ---(_)                    ",
            " _/  ---  \\                    ",
            "(_) |   |                      ",
            "  \\  --- _/                     ",
            "     ---(_)                    ",
            "                               ",
            "       .--.                    ",
            "      |o_o |                   ",
            "      |:_/ |                   ",
            "     //   \\ \\                   ",
            "    (|     | )                 "
        ],
        'arch': [
            "                   -`           ",
            "                  .o+`          ",
            "                 `ooo/           ",
            "                `+oooo:          ",
            "               `+oooooo:         ",
            "               -+oooooo+:        ",
            "             `/:-:++oooo+:       ",
            "            `/++++/+++++++:      ",
            "           `/++++++++++++++:     ",
            "          `/+++++++++++++++/     ",
            "         ./ooosssso++osssssso+`  ",
            "        .oossssso-````/ossssss+` "
        ],
        'linux': [
            "    .---.                      ",
            "   /     \\                     ",
            "   \\.@-@./                     ",
            "   /`\\_/`\\                      ",
            "  //  _  \\\\                     ",
            " | \\     )|_                   ",
            "/`\\_`>  <_/ \\                   ",
            "\\__/'---'\\__/                  "
        ]
    }
    return arts.get(distro, arts['linux'])

def main():
    """Основная функция"""
    info = get_info()
    distro = get_distro()
    art = get_ascii_art(distro)
    
    # Информация для отображения
    info_lines = [
        f"{info['user']}@{info['host']}",
        "-------------",
        f"OS: {info['os']}",
        f"Kernel: {info['kernel']}",
        f"Uptime: {info['uptime']}",
        f"Shell: {info['shell']}",
        f"CPU: {info['cpu']}",
        f"Memory: {info['memory']}",
        f"Disk: {info['disk']}",
        ""
    ]
    
    # Дополняем информацию до длины арта
    while len(info_lines) < len(art):
        info_lines.append("")
    
    # Выводим арт и информацию рядом (без цветов)
    for i, art_line in enumerate(art):
        info_line = info_lines[i] if i < len(info_lines) else ""
        print(f"{art_line} {info_line}")

def cli():
    """Entry point для консольной команды"""
    main()

if __name__ == "__main__":
    main()
