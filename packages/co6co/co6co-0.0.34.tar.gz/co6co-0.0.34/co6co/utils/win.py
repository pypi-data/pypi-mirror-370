import subprocess


def execute_command(command):
    """
    执行执行 命令 比如：command = 'netstat -ano | findstr "LISTENING"'
    """
    try:
        # 使用 subprocess.run 执行命令，stdout 设置为 PIPE 以捕获输出
        # result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        result = subprocess.run(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # 检查命令是否成功执行
        if result.returncode == 0:
            # 如果命令成功，打印或返回标准输出
            print(result.stdout)
            return result.stdout
        else:
            # 如果命令失败，打印错误信息
            print(f"Error executing command: {result.stderr}")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def parse_netstat_output(output: str, resultIndex: int = -1) -> list[str] | None:
    """
    解析 netstat 命令的输出
    """
    result_processes = []
    if output == None:
        return None
    lines = output.strip().split('\n')
    for line in lines:
        parts = line.split()
        if len(parts) > 0:
            result = parts[resultIndex]
            result_processes.append(result)
    return result_processes
