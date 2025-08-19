import os

# 读取文件内容
def read_file_content(file_path: str) -> str:
    with open(file_path, 'r') as file:
        return file.read()

# 获取指定目录下，时间戳最新的、以build.log结尾的文件
def get_latest_build_log_file(directory: str) -> str:
    # 列出目录下所有以build.log结尾的文件
    build_log_files = [f for f in os.listdir(directory) if f.endswith('.build.log')]
    
    # 按文件名排序，最新的在最后
    build_log_files.sort()
    
    # 返回最新的文件
    return os.path.join(directory, build_log_files[-1]) if build_log_files else None

# 读取指定目录下，时间戳最新的、以build.log结尾的文件内容
def read_latest_build_log_content(directory: str) -> str:
    latest_build_log_file = get_latest_build_log_file(directory)
    if latest_build_log_file:
        return read_file_content(latest_build_log_file)
    return ""

# 获取所有行中包含ERROR: 和 error: 的行
def get_all_error_lines(file_content: str) -> list[str]:
    return [line for line in file_content.splitlines() if "ERROR: " in line or "error: " in line]

# 提取一行内容中，在.jojo/repos/之后、/之前的内容
def extract_repo_name(line: str) -> str:
    """
    提取一行内容中，在.jojo/repos/之后、/之前的内容，如果没有.jojo/repos则返回空字符串
    :param line: 包含repo_name的行
    :return: 提取到的repo_name
    """
    if ".jojo/repos/" not in line:
        return ""
    start_index = line.find(".jojo/repos/") + len(".jojo/repos/")
    end_index = line.find("/", start_index)
    return line[start_index:end_index] if start_index != -1 and end_index != -1 else ""

def compress_logs(log_dir: str) -> str:
    """
    压缩指定目录下的所有日志文件为 zip 格式。
    :param log_dir: 日志文件所在目录
    :param output_path: 压缩后的输出路径
    :return: 压缩文件的路径
    """
    import os
    output_path = os.path.join(log_dir, "logs.zip")
    try:
        # 实现压缩逻辑
        import zipfile
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(log_dir):
                for file in files:
                    if file.endswith('.log'):
                        zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), log_dir))
        return f"日志文件已压缩至：{output_path}"
    except Exception as e:
        return f"压缩日志时出错：{str(e)}"

def get_git_user_email() -> str:
    """
    获取当前系统的 Git 用户邮箱。
    :return: Git 用户邮箱
    """
    try:
        email = subprocess.check_output(["git", "config", "user.email"], text=True).strip()
        return email
    except subprocess.CalledProcessError:
        return "未找到 Git 用户邮箱"

def parse_symbol_name(origin_symbol_name: str) -> str:
    """
    解析符号名
    :param origin_symbol_name: 原始符号名
    :return: 解析后的符号名
    """
    # 目前只解析c++和objc符号
    # 如果origin_symbol_name以_OBJC_CLASS_$_开头，去掉_OBJC_CLASS_$_后返回
    if origin_symbol_name.startswith("_OBJC_CLASS_$_"):
        return origin_symbol_name[len("_OBJC_CLASS_$_"):]
    # 调用c++filt解析符号
    try:
        symbol_name = subprocess.check_output(["c++filt", origin_symbol_name], text=True).strip()
        return symbol_name
    except subprocess.CalledProcessError:
        return origin_symbol_name
