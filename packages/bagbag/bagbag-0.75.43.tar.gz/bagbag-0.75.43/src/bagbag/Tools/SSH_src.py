import stat
import paramiko
from .. import Os


#print("load " + '/'.join(__file__.split('/')[-2:]))

class SSH():
    def __init__(self, host:str, port:int=None, user:str=None, password:str=None, pkey:str=None) -> None:
        """
        If you have a password, use it; if you have a private key, use it; 
        if you have neither, 尝试从~/.ssh/config读取, 如果没有读取默认的~/.ssh/id_rsa
        如果都没有, 扔异常
        支持使用config的配置, 例如端口, 主机名, 用户名, 私钥位置
        
        :param host: The hostname or IP address of the remote server
        :type host: str
        :param port: The port number of the SSH server. The default is 22, defaults to 22
        :type port: int (optional)
        :param user: The username to log in as
        :type user: str
        :param password: The password for the user
        :type password: str
        :param pkey: The path to the private key file
        :type pkey: str
        """
        self.ssh = paramiko.SSHClient()
        # 自动接收Host Key
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.sshcfg = paramiko.SSHConfig()
        # 载入~/.ssh/config 
        if Os.Getenv("HOME"):
            cfgpath = Os.Path.Join(Os.Getenv("HOME"), ".ssh/config")
            if Os.Path.Exists(cfgpath):
                self.sshcfg.parse(open(cfgpath))

        hostcfg = self.sshcfg.lookup(host)

        # 用配置文件解析一下host的ip, 如果配置文件没写就用传入的参数
        host = hostcfg["hostname"]
        # print(f"host: {host}")
        
        # 如果没有设置user
        if not user:
            # 读取配置文件的user
            if "user" in hostcfg:
                user = hostcfg["user"]
            else:
                # 如果没有配置文件的user, 那么使用当前登录的用户
                user = Os.GetLoginUserName()
        # print(f"user: {user}")
        
        if not port:
            if 'port' in hostcfg:
                port = hostcfg["port"]
            else:
                port = 22
        # print(f"port: {port}")

        # print(f"identityfile: {hostcfg['identityfile']}")

        # import ipdb 
        # ipdb.set_trace()

        # 如果有设置密码, 就用密码登录
        if password:
            self.ssh.connect(hostname=host, port=port, username=user, password=password) 
        else:
            # 如果没有设置pkey, 就找找
            if not pkey:
                # 如果配置文件有指定就用配置文件的
                if "identityfile" in hostcfg:
                    pkey = hostcfg['identityfile'][-1]
                    # 以下代码多余, 默认会是绝对路径
                    # if pkey.startswith("~"):
                    #     if Os.Getenv("HOME"):
                    #         pkey = Os.Path.Join(Os.Getenv("HOME"), pkey[1:])
                else:
                    # 如果有设置家目录就找默认的
                    if Os.Getenv("HOME"):
                        pkey = Os.Path.Join(Os.Getenv("HOME"), ".ssh/id_rsa")
                    else:
                        # 实在什么凭证都没有, 就抛异常
                        raise Exception("需要指定密码(password)或者私钥(pkey)")
            
            # print(f"pkey: {pkey}")
            privateKey = paramiko.RSAKey.from_private_key_file(pkey)
            self.ssh.connect(hostname=host, port=port, username=user, pkey=privateKey)

        try:
            self.sftp = self.ssh.open_sftp()
        except:
            self.sftp = None 
    
    def sftpcheck(func): # func是被包装的函数
        def ware(self, *args, **kwargs): # self是类的实例
            if self.sftp:
                res = func(self, *args, **kwargs)
                return res
            else:
                raise Exception("服务器不支持SFTP")

        return ware

    def GetOutput(self, command:str) -> str:
        stdin, stdout, stderr = self.ssh.exec_command(command)
        res, err = stdout.read(), stderr.read()
        res = res + err 
        res = res.decode("utf-8")
        return res
    
    def Close(self):
        self.ssh.close()

    @sftpcheck
    def Upload(self, localpath:str, remotepath:str=None):
        if not remotepath:
            remotepath = Os.Path.Basename(localpath)

        self.sftp.put(localpath, remotepath)

    @sftpcheck
    def Download(self, remotepath:str, localpath:str=None):
        if not localpath:
            localpath = Os.Path.Basename(remotepath)

        self.sftp.get(remotepath, localpath) 

    @sftpcheck
    def FileInfo(self, filepath:str):
        st = self.sftp.stat(filepath)
        info = {
            "size": st.st_size,
            "atime": st.st_atime,
            "mtime": st.st_mtime,
            "uid": st.st_uid, 
            "gid": st.st_gid, 
            "isdir": stat.S_ISDIR(st.st_mode)
        }
        return info

    @sftpcheck
    def ListDir(self, dirpath:str=".") -> dict:
        files = {}
        for f in self.sftp.listdir_attr(dirpath):
            files[f.filename] = {
                "size": f.st_size,
                "atime": f.st_atime,
                "mtime": f.st_mtime,
                "uid": f.st_uid, 
                "gid": f.st_gid, 
                "isdir": stat.S_ISDIR(f.st_mode)
            }
        return files 
    
if __name__ == "__main__":
    ssh = SSH("docker")
    # ssh = SSH("192.168.1.224")
    # ssh = SSH("192.168.1.1")

    o = ssh.GetOutput("ls -l")
    print(o)

    files = ssh.ListDir()
    print(files)