import os
import shutil
import zipfile
import time
import paramiko
from scp import SCPClient

def upload_img(local_path, remote_path, host, port, username, password):

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    ssh_client.connect(host, port, username, password)
    scpclient = SCPClient(ssh_client.get_transport(), socket_timeout=5.0)
    try:
        scpclient.put(local_path, remote_path)
    except FileNotFoundError as e:
        print(e)
        print("系统找不到指定文件" + local_path)
    else:
        print("文件上传成功")
        os.remove(local_path)
    ssh_client.close()


class FileMoveHandler():
    def __init__(self,conn_list):
        self.host_name = conn_list[0]
        self.port = conn_list[1]
        self.user_name = conn_list[2]
        self.password = conn_list[3]
        self.remote_path = conn_list[4]

    def start(self, filename):
        """
        文件处理逻辑
        """
        try:
            # 文件名、文件路径
            filename_without_suffix = filename
            source_file_path = watch_folder + filename
            
            # 定义压缩包的名字
            current_time=time.strftime('%Y%m%d%H%M%S')
            target_file_path = watch_folder + filename_without_suffix + "."  + current_time
            compress_file_path = watch_folder + filename_without_suffix + "."  + current_time + ".zip"

            # 移动、压缩
            print("开始重命名文件")
            shutil.move(source_file_path, target_file_path)
            print("重命名文件已结束，准备进行压缩")
            zfile = zipfile.ZipFile(target_file_path + ".zip","w")
            zfile.write(target_file_path)
            zfile.close()
            print("压缩结束，删除原文件")
            os.remove(target_file_path)
            print("开始上传")
            upload_img(compress_file_path, self.remote_path, self.host_name, self.port, self.user_name, self.password)
        except Exception as e:
            print("文件预处理失败，错误原因:", str(e.args))

if __name__ == "__main__":
    # 监听的文件夹目录
    env_dist = os.environ
    watch_folder = env_dist.get("dump_dir")

    # 监听文件名称
    watch_filename = env_dist.get("dump_file")

    # scp 推送的服务器信息
    conn_list = [env_dist.get("scp_host"),env_dist.get("scp_port"),env_dist.get("scp_user"),env_dist.get("scp_password"),env_dist.get("scp_remote_dir")]

    move_handler = FileMoveHandler(conn_list)

    try: 
        while True:
            if os.path.exists(watch_folder + watch_filename):
                f_info = os.stat(watch_folder + watch_filename).st_ctime
                time.sleep(3)
                c_info = os.stat(watch_folder + watch_filename).st_ctime
                if not f_info == c_info:
                    print(time.strftime("%Y-%m-%d %X"),"发现监控文件且文件正在被写入")
                    continue
                print(time.strftime("%Y-%m-%d %X"),"发现监控文件且文件已经写完,准备上传")
                start = time.time()
                move_handler.start(watch_filename)
                end = time.time()
                print(time.strftime("%Y-%m-%d %X"),f"文件打包上传共计用时: {end-start:.3f} s")
    except Exception as e:
        print(e)
