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
    """Получает расширенную системную информацию"""
    info = {}
    
    # Основная информация
    info['user'] = run_bash_command('whoami')
    info['host'] = run_bash_command('hostname')
    
    # OS информация
    info['os'] = run_bash_command('cat /etc/os-release | grep "PRETTY_NAME" | cut -d\'"\' -f2')
    info['arch'] = run_bash_command('uname -m')
    
    # Хост информация
    info['host_model'] = run_bash_command('cat /sys/devices/virtual/dmi/id/product_name 2>/dev/null || echo "Unknown"')
    
    # Ядро
    info['kernel'] = run_bash_command('uname -r')
    
    # Время работы
    info['uptime'] = run_bash_command('uptime -p | sed \'s/up //\'')
    
    # Пакеты
    dpkg_count = run_bash_command('dpkg -l 2>/dev/null | grep "^ii" | wc -l')
    info['packages'] = f"{dpkg_count} (dpkg)" if dpkg_count != "N/A" else "N/A"
    
    # Shell с версией
    shell_name = run_bash_command('basename "$SHELL"')
    shell_version = run_bash_command('$SHELL --version 2>/dev/null | head -n1 | grep -o "[0-9]\\+\\.[0-9]\\+\\.[0-9]\\+" | head -n1')
    info['shell'] = f"{shell_name} {shell_version}" if shell_version != "N/A" else shell_name
    
    # Терминал
    terminal = run_bash_command('echo $TTY')
    info['terminal'] = terminal if terminal and terminal != "N/A" else "/dev/pts/?"
    
    # CPU с частотой
    cpu_model = run_bash_command('cat /proc/cpuinfo | grep "model name" | head -n1 | cut -d: -f2 | sed "s/^ *//"')
    cpu_cores = run_bash_command('nproc')
    cpu_freq = run_bash_command('cat /proc/cpuinfo | grep "cpu MHz" | head -n1 | cut -d: -f2 | sed "s/^ *//" | awk "{printf \\"%.2f\\", $1/1000}"')
    info['cpu'] = f"{cpu_cores} x {cpu_model}"
    if cpu_freq != "N/A" and cpu_freq != "":
        info['cpu'] += f" @ {cpu_freq} GHz"
    
    # GPU
    gpu = run_bash_command('lspci 2>/dev/null | grep -i vga | cut -d: -f3 | sed "s/^ *//" | head -n1')
    if gpu == "N/A" or gpu == "":
        gpu = run_bash_command('lspci 2>/dev/null | grep -i display | cut -d: -f3 | sed "s/^ *//" | head -n1')
    info['gpu'] = gpu
    
    # Память с процентами
    mem_used = run_bash_command('free -h | awk \'/^Mem:/ {print $3}\'')
    mem_total = run_bash_command('free -h | awk \'/^Mem:/ {print $2}\'')
    mem_used_kb = run_bash_command('free | awk \'/^Mem:/ {print $3}\'')
    mem_total_kb = run_bash_command('free | awk \'/^Mem:/ {print $2}\'')
    if mem_used_kb != "N/A" and mem_total_kb != "N/A" and mem_total_kb.isdigit() and int(mem_total_kb) > 0:
        mem_percent = int((int(mem_used_kb) * 100) / int(mem_total_kb))
        info['memory'] = f"{mem_used} / {mem_total} ({mem_percent}%)"
    else:
        info['memory'] = f"{mem_used} / {mem_total}"
    
    # Swap
    swap_used = run_bash_command('free -h | awk \'/^Swap:/ {print $3}\'')
    swap_total = run_bash_command('free -h | awk \'/^Swap:/ {print $2}\'')
    swap_used_kb = run_bash_command('free | awk \'/^Swap:/ {print $3}\'')
    swap_total_kb = run_bash_command('free | awk \'/^Swap:/ {print $2}\'')
    if swap_used_kb != "N/A" and swap_total_kb != "N/A" and swap_total_kb.isdigit() and int(swap_total_kb) > 0:
        swap_percent = int((int(swap_used_kb) * 100) / int(swap_total_kb))
        info['swap'] = f"{swap_used} / {swap_total} ({swap_percent}%)"
    else:
        info['swap'] = f"{swap_used} / {swap_total}"
    
    # Диск с файловой системой
    disk_used = run_bash_command('df -h / | awk \'NR==2 {print $3}\'')
    disk_total = run_bash_command('df -h / | awk \'NR==2 {print $2}\'')
    disk_percent = run_bash_command('df -h / | awk \'NR==2 {print $5}\' | sed \'s/%//\'')
    disk_fs = run_bash_command('df -T / | awk \'NR==2 {print $2}\'')
    info['disk'] = f"{disk_used} / {disk_total} ({disk_percent}%) - {disk_fs}"
    
    # IP адрес
    local_ip = run_bash_command('hostname -I | awk \'{print $1}\'')
    interface = run_bash_command('ip route | grep default | awk \'{print $5}\' | head -n1')
    if interface != "N/A" and interface != "":
        info['local_ip'] = f"{local_ip} ({interface})"
    else:
        info['local_ip'] = local_ip
    
    # Локаль
    info['locale'] = run_bash_command('echo $LANG')
    
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
    """Возвращает ASCII арт шириной до 40 символов"""
    arts = {
        'debian': [
            "           ___________                  ",
            "        .##############.               ",
            "      .##################.             ",
            "     #####################             ",
            "    #######################            ",
            "   ######################.             ",
            "  .######################              ",
            "  ########################             ",
            "  #########################            ",
            "  #########################            ",
            "  ##########################           ",
            "  ##########################           ",
            "   #########################           ",
            "    #######################            ",
            "     #####################             ",
            "      .##################.             ",
            "        .##############.               ",
            "           ___________                  ",
            "                                       ",
            "            D E B I A N                "
        ],
        'ubuntu': [
            "            .oyhhs:                    ",
            "         .ohNMMMMMMNho.               ",
            "       .dMMMMMMMMMMMMMMd.             ",
            "      +MMMMMMMMMMMMMMMMMMh            ",
            "     sMMMMMMMMMMMMMMMMMMM/            ",
            "    sMMMMMMMMMMMMMMMMMMMs             ",
            "   +MMMMMMMMMMMMMMMMMMMM/             ",
            "   dMMMMMMMMMMMMMMMMMMMM              ",
            "   dMMMMMMMMMMMMMMMMMMMM              ",
            "   +MMMMMMMMMMMMMMMMMMMM/             ",
            "    sMMMMMMMMMMMMMMMMMMMs             ",
            "     sMMMMMMMMMMMMMMMMMMM/            ",
            "      +MMMMMMMMMMMMMMMMMMh            ",
            "       .dMMMMMMMMMMMMMMd.             ",
            "         .ohNMMMMMMNho.               ",
            "            .oyhhs:                   ",
            "                                      ",
            "           U B U N T U                "
        ],
        'arch': [
            "                   -`                 ",
            "                  .o+`                ",
            "                 `ooo/                ",
            "                `+oooo:               ",
            "               `+oooooo:              ",
            "               -+oooooo+:             ",
            "             `/:-:++oooo+:            ",
            "            `/++++/+++++++:           ",
            "           `/++++++++++++++:          ",
            "          `/+++oooooooooooo/`         ",
            "         ./ooosssso++osssssso+`       ",
            "        .oossssso-````/ossssss+`      ",
            "       -osssssso.      :ssssssso.     ",
            "      :osssssss/        osssso+++.    ",
            "     /ossssssss/        +ssssooo/-    ",
            "   `/ossssso+/:-        -:/+osssso+-  ",
            "  `+sso+:-`                 `.-/+oso: ",
            " `++:.                           `-/+/",
            " .`                                 `/",
            "                                      ",
            "             A R C H                  "
        ],
        'linux': [
            "               .--.                   ",
            "              |o_o |                  ",
            "              |:_/ |                  ",
            "             //   \\ \\                 ",
            "            (|     | )                ",
            "           /'\\_ _/`\\                  ",
            "           \\___)=(___/                 ",
            "                                      ",
            "                .-.                   ",
            "               (o o)                  ",
            "              ooO-(_)-Ooo             ",
            "                                      ",
            "           L I N U X                  ",
            "                                      ",
            "      \"The power of open source\"      ",
            "                                      "
        ]
    }
    return arts.get(distro, arts['linux'])

def main():
    """Основная функция"""
    info = get_info()
    distro = get_distro()
    art = get_ascii_art(distro)
    
    # Расширенная информация для отображения
    user_host = f"{info['user']}@{info['host']}"
    separator = "-" * len(user_host)
    
    info_lines = [
        user_host,
        separator,
        f"OS: {info['os']} {info['arch']}",
        f"Host: {info['host_model']}",
        f"Kernel: Linux {info['kernel']}",
        f"Uptime: {info['uptime']}",
        f"Packages: {info['packages']}",
        f"Shell: {info['shell']}",
        f"Terminal: {info['terminal']}",
        f"CPU: {info['cpu']}",
        f"GPU: {info['gpu']}",
        f"Memory: {info['memory']}",
        f"Swap: {info['swap']}",
        f"Disk (/): {info['disk']}",
        f"Local IP: {info['local_ip']}",
        f"Locale: {info['locale']}",
    ]
    
    # Выводим арт и информацию рядом до конца арта
    for i, art_line in enumerate(art):
        info_line = info_lines[i] if i < len(info_lines) else ""
        print(f"{art_line} {info_line}")
    
    # Если информации больше чем строк в арте, выводим остальное ниже
    if len(info_lines) > len(art):
        print()  # Пустая строка для разделения
        for i in range(len(art), len(info_lines)):
            print(info_lines[i])

def cli():
    """Entry point для консольной команды"""
    main()

if __name__ == "__main__":
    main()
