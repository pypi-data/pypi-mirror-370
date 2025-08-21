from vncdotool import api
from . import RateLimit

class VNC:
    def __init__(self, host:str, port:int, password:str=None, ratelimit:str="30/m"):
        self.client = api.connect(f"{host}::{port}", password=password)
        self.rl = RateLimit('30/m')
    
    def MouseMove(self, x, y, step:int=None):
        """移动鼠标到指定位置, step是拖动的步长, 不设置则一步到位"""
        self.rl.Take()
        if step == None:
            self.client.mouseMove(x, y)
        else:
            self.client.mouseDrag(x, y, step)

        return self
    
    def MouseClickLeft(self):
        """点击鼠标左键"""
        self.rl.Take()
        self.client.mousePress(1)

        return self
    
    def MouseClickRight(self):
        """点击鼠标右键"""
        self.rl.Take()
        self.client.mousePress(3)

        return self
    
    def MouseDownLeft(self):
        """按下鼠标左键"""
        self.rl.Take()
        self.client.mouseDown(1)

        return self
    
    def MouseUpLeft(self):
        """放开鼠标左键"""
        self.rl.Take()
        self.client.mouseUp(3)

        return self

    def MouseDownRight(self):
        """按下鼠标右键"""
        self.rl.Take()
        self.client.mouseDown(3)

        return self
    
    def MouseUpLeft(self):
        """放开鼠标右键"""
        self.rl.Take()
        self.client.mouseUp(1)

        return self

    def Shift(self, key:str):
        """按下并放开shift-{key}"""
        self.rl.Take()
        self.client.keyPress(f"shift-{key}")

        return self
    
    def Ctrl(self, key:str):
        """按下并放开ctrl-{key}"""
        self.rl.Take()
        self.client.keyPress(f"ctrl-{key}")

        return self

    def CtrlAltDel(self):
        """按下并放开 ctrl-alt-del"""
        self.rl.Take()
        self.client.keyPress(f"ctrl-alt-del")

        return self

    def KeyPress(self, key:str):
        """
        按下并放开按键
        举例来说, key可以是
        1. a
        2. 5
        3. .
        4. enter
        5. shift-a
        6. ctrl-C
        7. ctrl-alt-del
        """
        self.rl.Take()
        self.client.keyPress(key)

        return self

    def KeyDown(self, key:str):
        """
        按下按键
        举例来说, key可以是
        1. a
        2. 5
        3. .
        4. enter
        5. shift-a
        6. ctrl-C
        7. ctrl-alt-del
        """
        self.rl.Take()
        self.client.keyDown(key)

        return self
    
    def KeyUp(self, key:str):
        """
        放开按键
        举例来说, key可以是
        1. a
        2. 5
        3. .
        4. enter
        5. shift-a
        6. ctrl-C
        7. ctrl-alt-del
        """
        self.rl.Take()
        self.client.keyUp(key)

        return self
    
    def CaptureScreen(self, fname:str):
        """保存屏幕截图到文件, 图片文件支持jpg,jpeg,gif,png结尾"""
        self.rl.Take()
        self.client.refreshScreen()
        self.client.captureScreen(fname)

        return self

    def CaptureRegion(self, fname:str, x:int, y:int, w:int, h:int):
        """保存屏幕的区域的截图到文件"""
        self.rl.Take()
        self.client.refreshScreen()
        self.client.captureRegion(fname, x, y, w, h)

        return self

    def Input(self, string:str):
        """通过模拟按键输入字符串"""
        self.rl.Take()
        for c in string:
            self.keyPress(c)

        return self

    def Close(self):
        """关闭VNC连接"""
        self.client.disconnect()
        api.shutdown()

# 示例用法
if __name__ == "__main__":
    vnc_host = '192.168.1.5::5900'
    vnc_password = None
    x = 234
    y = 234

    client = VNC(vnc_host, vnc_password)
    client.MouseMove(x, y)
    client.MouseClickLeft()
    client.MouseClickRight()
    client.Ctrl('c')
    client.Input('Hello, World!')
    client.Key('c')
    client.CaptureScreen("vnc.jpg")
    client.Close()