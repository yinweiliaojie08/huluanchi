import os

from watchdog.observers import Observer
from watchdog.events import *
import ntpath
import shutil
import zipfile
import time

def get_filename(filepath):
    """
    根据文件夹目录，获取文件名称（待后缀）
    :param filepath:
    :return:
    """
    return ntpath.basename(filepath)


# 文件处理，只监控新创建的文件，文件删除、修改动作直接略过
class FileMoveHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)

    def on_moved(self, event):
        pass

    #  新建文件
    def on_created(self, event):
        if event.is_directory:
            pass
        else:
            filename = get_filename(event.src_path)

            # 如果属于watch_tags列表中的项目压缩包，触发更新文件夹的操作
            if filename in watch_tags:
                self.start(filename,days)

    def on_deleted(self, event):
        pass

    def on_modified(self, event):
        if event.is_directory:
            pass
        else:
            pass

    def start(self, filename, days):
        """
        文件处理逻辑
        """
        try:
            # 文件名不带后缀
            filename_without_suffix = filename.split(".")[0]

            # 源文件路径（压缩包文件）
            source_file_path = watch_folder + filename

            # 目标文件路径（压缩包文件）
            target_file_path = target_folder + filename

            # 目标项目文件夹（目标项目）
            target_project_path = target_folder + filename_without_suffix
            
            #备份文件名称
            current_time=time.strftime('%Y%m%d%H%M%S')
            target_project_bak_path = backup_dir + filename_without_suffix + "."  + current_time + ".bak"

            # ---------------- 开始文件更新 ------------------------------------------------------
            print(f"拷贝源目录{source_file_path},目标文件夹:{target_folder},备份目录{backup_dir}")
            print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))

            # 原文件备份
            if os.path.exists(target_project_path):
                shutil.move(target_project_path, target_project_bak_path)
                os.mkdir(target_project_path)
            else:
                os.mkdir(target_project_path)
            
            # 删除旧的备份文件
            bakfileNames = sorted(os.listdir(backup_dir),key=lambda x: os.path.getmtime(os.path.join(backup_dir, x)),reverse=True)
            baklist = []
            for bakname in bakfileNames:
                if filename_without_suffix in bakname:
                    fullbakname_path = os.path.join(backup_dir, bakname)
                    baklist.append(fullbakname_path)
            if baklist:
                for bakname in baklist[days:]:
                    shutil.rmtree(bakname)
            
            # 删除旧的压缩包
            if os.path.exists(target_file_path):
                os.remove(target_file_path)
            
            # 移动压缩包至项目目录
            shutil.move(source_file_path, target_folder)
            print(f"项目{filename_without_suffix}移动成功！")

        except Exception as e:
            print("文件预处理失败，错误原因:", str(e.args))


# 解压
class FileUnzipHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)

    def on_created(self, event):
        if event.is_directory:
            pass
        else:
            filename = get_filename(event.src_path)

            # 如果属于watch_tags列表中的项目压缩包，触发解压压缩文件的操作
            if filename in watch_tags:
                self.start(filename)

    def on_modified(self, event):
        if event.is_directory:
            pass
        else:
            filename = get_filename(event.src_path)
            if filename in watch_tags:
                self.start(filename)

    def start(self, filename):
        # 文件名不带后缀
        filename_without_suffix = filename.split(".")[0]

        # 目标文件路径（压缩包文件）
        target_file_path = target_folder + filename

        # 目标项目文件夹（目标项目）
        target_project_path = target_folder + filename_without_suffix
        r = zipfile.is_zipfile(target_file_path)
        if r:
            print(f"项目{target_file_path}开始解压！")
            print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
            fz = zipfile.ZipFile(target_file_path, 'r')
            for file in fz.namelist():
                # 写入到这个文件夹下
                fz.extract(file, target_folder)
            print(f"项目{target_file_path}已解压成功！")
        else:
            pass

        # 删除压缩包
        if os.path.exists(target_file_path):
            os.remove(target_file_path)



if __name__ == "__main__":
    # 待监听的文件夹目录
    watch_folder = "/tmp/"

    # 项目目标文件夹目录
    target_folder = "/data/frontend/"
    
    # 备份文件目录
    backup_dir = "/data/backup/"

    # 备份保留天数
    days = 2

    # 监听文件夹名称，即：项目压缩包名称
    watch_tags = ['proj1.zip',"proj2.zip","proj3.zip"]

    # 创建一个监听器，用来监听文件夹目录
    observer = Observer()

    # 创建两个事件处理对象
    move_handler = FileMoveHandler()
    unzip_handler = FileUnzipHandler()

    # 启动监控任务
    # 参数分别是：观察者、监听目录、是否监听子目录
    observer.schedule(move_handler, watch_folder, True)
    observer.schedule(unzip_handler, target_folder, True)
    observer.start()
    try: 
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

