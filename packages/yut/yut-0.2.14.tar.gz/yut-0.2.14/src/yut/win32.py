# -*- win32.py: python ; coding: utf-8 -*-
# 与Win32环境相关的工具
import hashlib
import os
import platform
import re
import subprocess
import sys
import uuid

import win32com
import win32com.client


def create_short_cut(lnk_name):
    usr_home = os.path.expanduser('~')
    exe_name = os.path.realpath(sys.executable)
    work_dir = os.path.split(exe_name)[0]

    desktop = fr'{usr_home}\Desktop'  # 桌面文件夹的完整路径
    shortcut_path = os.path.join(desktop, f'{lnk_name}.lnk')  # 要生成的快捷方式路径及文件名
    target = icon = fr"{exe_name}"  # 要生成快捷方式的原文件路径

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)  # 生成快捷方式文件
    shortcut.Targetpath = target  # 目标文件路径
    shortcut.WorkingDirectory = work_dir  # 起始工作路径
    shortcut.IconLocation = icon  # 指定图标
    shortcut.save()  # 保存快捷方式文件


# 取主板smBIOS信息：主板UUID是很多授权方法和微软官方都比较推崇的方法，即便重装系统UUID应该也不会变
def get_UUID():
    for line in os.popen('wmic csproduct get UUID'):
        text = line.rstrip()
        if text.lower().startswith('uuid'):
            continue
        if len(text) > 2:
            return text
    return None


def get_cpuid():
    """
    取CPU ID(仅限Windows系统)
    :return:
    """
    for line in os.popen('wmic cpu get processorID'):
        text = line.rstrip()
        if text.lower().startswith('processorid'):
            continue
        if len(text) > 2:
            return text
    return None


def write_settings(key, value, org_name=None, app_name=None):
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QSettings
    if org_name is None:
        org_name = 'nstc'
    if app_name is None:
        app_name = QApplication.instance().applicationName()
    settings = QSettings(org_name, app_name)
    settings.setValue(key, value)


def read_settings(key, default_value=None, org_name=None, app_name=None):
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QSettings
    if org_name is None:
        org_name = 'nstc'
    if app_name is None:
        app_name = QApplication.instance().applicationName()
    settings = QSettings(org_name, app_name)
    return settings.value(key, default_value)


def set_process_user_model_id(app_user_model_id):
    """
    设置当前进程的外部名称(任务栏唤起看到的名称)
    指定应用程序定义的唯一应用程序用户模型 ID (AppUserModelID) ，用于标识任务栏的当前进程。
    此标识符允许应用程序将其关联的进程和窗口分组到单个任务栏按钮下。
    :param app_user_model_id:
    :return:
    """
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_user_model_id)


def get_profile(org_name=None, app_name=None):
    """
    从注册表读取profile信息
    :param org_name: 注册表中的机构，默认为None时，机构名='yut'
    :param app_name: 注册表中的app,默认为None时使用当前应用程序的applicationName()
    :return: (用户名,注册邮箱,注册码) 分别对应reg.user,reg.mail,reg.code三个注册项
    """
    user = read_settings('reg.user', '', org_name=org_name, app_name=app_name)
    mail = read_settings('reg.mail', '', org_name=org_name, app_name=app_name)
    reg_code = read_settings('reg.code', org_name=org_name, app_name=app_name)
    return user, mail, reg_code


def write_profile(user, mail, reg_code, org_name=None, app_name=None):
    """
    向注册表中写入profile信息
    :param user: 用户名,存入"reg.user"注册项
    :param mail: 注册邮箱,存入"reg.mail"注册项
    :param reg_code: 注册码,存入"reg.code"注册项
    :param org_name: 注册表中的机构，默认为None时，机构名='yut'
    :param app_name: 注册表中的app,默认为None时使用当前应用程序的applicationName()
    :return:
    """
    write_settings('reg.user', user, org_name=org_name, app_name=app_name)
    write_settings('reg.mail', mail, org_name=org_name, app_name=app_name)
    write_settings('reg.code', reg_code, org_name=org_name, app_name=app_name)


def get_device_fingerprint():
    """获取组合设备指纹（SHA256哈希）"""
    identifiers = {
        "machine_id": get_machine_id(),
        "disk_serial": get_disk_serial(),
        "mac_address": get_primary_mac(),
        "bios_uuid": get_bios_uuid(),
        "cpu_id": get_cpu_id()
    }
    print(identifiers)
    # 拼接所有标识符并生成哈希
    combined = "&".join(f"{k}={v}" for k, v in identifiers.items() if v)
    return hashlib.sha256(combined.encode()).hexdigest()


# 下面是各独立标识符的获取方法
def get_machine_id():
    """获取操作系统生成的机器ID"""
    try:
        # Linux/Systemd系统
        if platform.system() == 'Linux':
            with open("/etc/machine-id") as f:
                return f.read().strip()

        # macOS
        elif platform.system() == 'Darwin':
            return subprocess.check_output(
                "ioreg -rd1 -c IOPlatformExpertDevice | awk '/IOPlatformUUID/'",
                shell=True
            ).decode().split('"')[-2]

        # Windows
        elif platform.system() == 'Windows':
            import winreg
            with winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Microsoft\Cryptography"
            ) as key:
                return winreg.QueryValueEx(key, "MachineGuid")[0]
    except:
        return None


def get_disk_serial():
    """获取系统盘序列号"""
    try:
        if platform.system() == 'Windows':
            cmd = 'wmic diskdrive where "Index=0" get SerialNumber'
            output = subprocess.check_output(cmd, shell=True).decode()
            return re.search(r'\b(\w{10,})\b', output).group(1).strip()
        elif platform.system() == 'Linux':
            # 获取根分区对应的物理磁盘
            root_dev = subprocess.check_output(
                "df / | tail -1 | awk '{print $1}'",
                shell=True
            ).decode().strip()
            disk = root_dev.replace("/dev/", "").rstrip("1234567890")

            # 读取序列号
            with open(f"/sys/block/{disk}/device/serial") as f:
                return f.read().strip()

        elif platform.system() == 'Darwin':
            output = subprocess.check_output(
                "diskutil info / | grep 'Device Identifier'",
                shell=True
            ).decode()
            disk = output.split(":")[1].strip()
            return subprocess.check_output(
                f"diskutil info {disk} | grep 'Device UUID'",
                shell=True
            ).decode().split(":")[1].strip()

    except Exception as e:
        print(e)
        return None


def get_primary_mac():
    """获取活动网络接口的MAC地址"""
    try:
        # 排除虚拟网卡和本地环回
        mac = uuid.getnode()
        if (mac >> 40) & 0xff == 0xfe:  # 排除本地生成地址
            return None
        return ':'.join(('%012X' % mac)[i:i + 2] for i in range(0, 12, 2))
    except:
        return None


def get_bios_uuid():
    """获取BIOS/UEFI UUID"""
    try:
        if platform.system() == 'Windows':
            import wmi
            c = wmi.WMI()
            return c.Win32_ComputerSystemProduct()[0].UUID

        elif platform.system() == 'Linux':
            with open("/sys/class/dmi/id/product_uuid") as f:
                return f.read().strip()

        elif platform.system() == 'Darwin':
            return subprocess.check_output(
                "ioreg -rd1 -c IOPlatformExpertDevice | grep IOPlatformUUID",
                shell=True
            ).decode().split('"')[-2]
    except:
        return None


def get_cpu_id():
    """获取CPU唯一标识"""
    try:
        if platform.system() == 'Windows':
            import wmi
            c = wmi.WMI()
            return c.Win32_Processor()[0].ProcessorId.strip()

        elif platform.system() == 'Linux':
            # 读取CPU信息
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if "model name" in line:
                        model = line.split(":")[1].strip()
                    elif "physical id" in line:
                        phys_id = line.split(":")[1].strip()
                return hashlib.sha256(f"{model}_{phys_id}".encode()).hexdigest()

        elif platform.system() == 'Darwin':
            return subprocess.check_output(
                "sysctl -n machdep.cpu.brand_string",
                shell=True
            ).decode().strip()

    except:
        return None


if __name__ == '__main__':
    gdf = get_device_fingerprint()
    print(gdf)
