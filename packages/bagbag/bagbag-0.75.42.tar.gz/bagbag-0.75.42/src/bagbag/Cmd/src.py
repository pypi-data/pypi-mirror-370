import subprocess
import typing 
import collections
import queue
import threading
import json
import subprocess
import shutil

# print("load cmd")

class ContinuousSubprocess:
    """
    Creates a process to execute a wanted command and
    yields a continuous output stream for consumption.
    """

    def __init__(self, command_string: str) -> None:
        """
        Constructor.

        :param command_string: A command to execute in a separate process.
        """
        self.__command_string = command_string
        self.__process: typing.Optional[subprocess.Popen] = None
        self.terminated = False

    @property
    def command_string(self) -> str:
        """
        Property for command string.

        :return: Command string.
        """
        return self.__command_string

    def Terminate(self) -> None:
        if not self.__process:
            raise ValueError('Process is not running.')

        # self.__process.terminate()
        self.__process.kill()
        self.terminated = True

    def Execute(
        self,
        shell: bool = True,
        path: typing.Optional[str] = None,
        max_error_trace_lines: int = 1000,
        *args,
        **kwargs,
    ) -> typing.Generator[str, None, None]:
        """
        Executes a command and yields a continuous output from the process.

        :param shell: Boolean value to specify whether to
        execute command in a new shell.
        :param path: Path where the command should be executed.
        :param max_error_trace_lines: Maximum lines to return in case of an error.
        :param args: Other arguments.
        :param kwargs: Other named arguments.

        :return: A generator which yields output strings from an opened process.
        """
        # Check if the process is already running (if it's set, then it means it is running).
        if self.__process:
            raise RuntimeError(
                'Process is already running. '
                'To run multiple processes initialize a second object.'
            )

        with subprocess.Popen(
            self.__command_string,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            shell=shell,
            cwd=path,
            *args,
            **kwargs,
        ) as process:

            # Indicate that the process has started and is now running.
            self.__process = process

            # Initialize a mutual queue that will hold stdout and stderr messages.
            q = queue.Queue()
            # Initialize a limited queue to hold last N of lines.
            dq = collections.deque(maxlen=max_error_trace_lines)

            # Create a parallel thread that will read stdout stream.
            stdout_thread = threading.Thread(
                target=ContinuousSubprocess.__read_stream, args=[process.stdout, q]
            )
            stdout_thread.start()

            # Create a parallel thread that will read stderr stream.
            stderr_thread = threading.Thread(
                target=ContinuousSubprocess.__read_stream, args=[process.stderr, q]
            )
            stderr_thread.start()

            # Run this block as long as our main process is alive or std streams queue is not empty.
            while (process.poll() is None) or (not q.empty()):
                try:
                    # Rad messages produced by stdout and stderr threads.
                    item = q.get(block=True, timeout=1)
                    dq.append(item)
                    yield item
                    if self.terminated == True:
                        return 
                except queue.Empty:
                    pass

            # Close streams.
            process.stdout.close()
            process.stderr.close()

            return_code = process.wait()

        # Make sure both threads have finished.
        stdout_thread.join(timeout=5)
        if stdout_thread.is_alive():
            raise RuntimeError('Stdout thread is still alive!')

        stderr_thread.join(timeout=5)
        if stderr_thread.is_alive():
            raise RuntimeError('Stderr thread is still alive!')

        # Indicate that the process has finished as is no longer running.
        self.__process = None

        if return_code:
            error_trace = list(dq)
            raise subprocess.CalledProcessError(
                returncode=return_code,
                cmd=self.__command_string,
                output=json.dumps(
                    {
                        'message': 'An error has occurred while running the specified command.',
                        'trace': error_trace,
                        'trace_size': len(error_trace),
                        'max_trace_size': max_error_trace_lines,
                    }
                ),
            )

    @staticmethod
    def __read_stream(stream: typing.IO[typing.AnyStr], queue: queue.Queue):
        try:
            for line in iter(stream.readline, ''):
                if line != '':
                    queue.put(line)
        # It is possible to receive: ValueError: I/O operation on closed file.
        except ValueError:
            return

# command = Os.Args[1]
# generator = ContinuousSubprocess(command).execute()

# for data in generator:
#     print(data)

def TailOutput(cmd:str) -> typing.Iterator[str]:
    for i in ContinuousSubprocess(cmd).Execute():
        if i[-1] == "\n":
            yield i[:-1]
        else:
            yield i

def GetStatusOutput(cmd:str, decodeerror:str="ignore") -> typing.Tuple[int, str]:
    """
    函数 `GetStatusOutput` 执行一个 shell 命令，并返回一个包含状态码和命令输出的元组。

    参数：
    - `cmd`：一个字符串，表示要在 shell 中执行的命令。它将被传递给 `subprocess.Popen` 函数，以在子进程中运行该命令。
    - `decodeerror`：在 `GetStatusOutput` 函数中，`decodeerror` 参数用于指定在将命令输出转换为字符串时如何处理解码错误。默认设置为 "ignore"，这意味着在解码过程中遇到的任何解码错误都将被忽略。可选strict

    返回：一个元组，包含一个表示命令执行状态的整数和一个表示命令输出的字符串。
    """
    tsk = subprocess.Popen(["sh", "-c", cmd],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    status = tsk.wait()

    return status, tsk.stdout.read().decode('utf-8', decodeerror)

def GetOutput(cmd:str, decodeerror:str='ignore') -> str:
    """
    `decodeerror` 参数用于指定在将命令输出转换为字符串时如何处理解码错误。默认设置为 "ignore"，这意味着在解码过程中遇到的任何解码错误都将被忽略。可选strict
    """
    _, output = GetStatusOutput(cmd, decodeerror)

    return output

def Exist(cmd:str) -> bool:
    return shutil.which(cmd) is not None

def Where(cmd:str) -> str:
    return shutil.which(cmd)

if __name__ == "__main__":
    print(Exist("ls"))