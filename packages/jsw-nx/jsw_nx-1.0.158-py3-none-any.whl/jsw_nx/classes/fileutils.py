import os
import shutil


class FileUtils:
    @classmethod
    def mkdir_p(cls, in_dir):
        """
        Create a directory and all parent directories.
        :param in_dir:
        :return:
        """

        if not os.path.isdir(in_dir):
            os.makedirs(in_dir, exist_ok=True)

    @classmethod
    def basename(cls, **kwargs):
        """
        Get the basename of a path.
        :param kwargs:
            - path: The path to get the basename from.
            - with_ext: Whether to include the extension in the basename.
        :return:
        """
        path = kwargs.get('path')
        with_ext = kwargs.get('with_ext', False)
        basen = os.path.basename(path)
        if with_ext:
            return basen
        return os.path.splitext(basen)[0]

    @classmethod
    def extname(cls, in_path):
        """
        Get the extension of a path.
        :param in_path:
        :return:
        """
        return os.path.splitext(in_path)[1]

    @classmethod
    def cd(cls, in_dir):
        """
        Change directory.
        :param in_dir:
        :return:
        """
        os.chdir(in_dir)

    @classmethod
    def pwd(cls):
        """
        Print the current working directory.
        :return:
        """
        return os.getcwd()

    @classmethod
    def ls(cls, in_dir="."):
        """
        List the contents of a directory.
        :param in_dir:
        :return:
        """
        return os.listdir(in_dir)

    @classmethod
    def mv(cls, src, dest):
        """
        Move a file or directory.
        :param src:
        :param dest:
        :return:
        """
        shutil.move(src, dest)

    @classmethod
    def rmdir(cls, in_dir):
        """
        Remove a directory.
        :param in_dir:
        :param opts:
        :return:
        """
        os.rmdir(in_dir)

    @classmethod
    def touch(cls, in_file):
        """
        Create a file.
        :param in_list:
        :param opts:
        :return:
        """
        open(in_file, 'a').close()

    @classmethod
    def cp_r(cls, src, dest):
        """
        Copy a file or directory recursively.
        :param src:
        :param dest:
        :param opts:
        :return:
        """
        if os.path.isfile(src):
            shutil.copy(src, dest)
        elif os.path.isdir(src):
            shutil.copytree(src, dest)

    @classmethod
    def isfile(cls, target):
        """
        Check if a file exists.
        """
        return os.path.isfile(target)

    @classmethod
    def isdir(cls, target):
        """
        Check if a dir exists.
        :param target:
        :return:
        """
        return os.path.isdir(target)

    @classmethod
    def rm(cls, target):
        """
        Remove a file or directory.
        :param target:
        :return:
        """
        if cls.exists(target):
            if cls.isfile(target):
                os.remove(target)
            elif cls.isdir(target):
                shutil.rmtree(target)

    @classmethod
    def exists(cls, target):
        """
        Check if a file or dir exists.
        :param target:
        :return:
        """
        return os.path.exists(target)

    @classmethod
    def gbk_to_utf8(cls, source, target, callback=None):
        """
        Convert GBK to UTF-8.
        :param source:
        :param target:
        :param callback:
        :return:
        """
        with open(source, "r", encoding="gbk") as src:
            with open(target, "w", encoding="utf-8") as dst:
                for line in src.readlines():
                    if callback:
                        line = callback(line)
                    dst.write(line)

    @classmethod
    def read_lines(cls, filename, **kwargs):
        """
        Read lines.
        :param filename:
        :param kwargs:
        :return:
        """
        flag = kwargs.get('flag', 'r')
        callback = kwargs.get('callback', lambda ln: ln.strip() if ln.strip() else None)
        handle = open(filename, flag)
        lines = handle.readlines()
        result = []
        for line in lines:
            res = callback(line)
            if res:
                result.append(callback(line))
        handle.close()
        return result

    @classmethod
    def read_file_content(cls, filename, **kwargs):
        """
        Read file content.
        :param filename:
        :param kwargs:
        :return:
        """
        flag = kwargs.get('flag', 'r')
        handle = open(filename, flag)
        content = handle.read()
        handle.close()
        return content
