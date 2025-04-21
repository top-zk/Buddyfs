import os
import subprocess

def convert_virtual_disk(input_file, output_file):
    """
    将虚拟磁盘文件转换为原始磁盘映像格式 (.img)
    
    参数:
        input_file (str): 输入虚拟磁盘文件路径（如 .qcow2 或 .vmdk 文件）
        output_file (str): 输出 .img 文件路径
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file is not exist: {input_file}")
    
    try:
        # 检查是否安装 qemu-img 工具
        subprocess.run(["qemu-img", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        raise EnvironmentError("qemu-img tools are not exit. Please install it.")
    
    # 执行 qemu-img 转换命令
    try:
        command = ["qemu-img", "convert", "-f", "vmdk", "-O", "raw", input_file, output_file]
        print(f"execute: {' '.join(command)}")
        subprocess.run(command, check=True)
        print(f"success, output: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"failure: {e.stderr.decode('utf-8')}")
        raise RuntimeError("qemu-img has error")

def main():
    # 输入和输出路径（替换为您的实际文件路径）
    input_file = "D:\\Virtual Machines\\leahuguan.vmdk"  # 输入虚拟磁盘文件路径  # 输入虚拟磁盘文件路径
    output_file = "D:\大学学术资料\大三\操作系統實驗\project\Result2\output\disk.img"    # 输出 .img 文件路径

    try:
        convert_virtual_disk(input_file, output_file)
    except Exception as e:
        print(f"error: {e}")

if __name__ == "__main__":
    main()