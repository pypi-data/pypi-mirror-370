import matplotlib.pyplot as plt
import io
from PIL import Image

def XY(
        x_values:list, 
        y_values:list, 
        sortByX:bool=True, 
        title:str="This is a title", 
        xlabel:str="X", 
        ylabel:str="Y", 
        connect_points:bool=True, 
        width:int=8, 
        height:int=6,
        savefilepath:str=None,
    ) -> bytes:
    """
    用matplotlib绘制不同的x值和y值，并返回JPEG格式图片的字节数组

    :param x_values: list of float, x 值
    :param y_values: list of float, y 值
    :param sortByX: 把X从小到大排序, 相应的调整Y的值顺序
    :param connect_points: bool, 是否连接y值的点
    :param width: int, 图片的宽度（英寸）
    :param height: int, 图片的高度（英寸）
    :return: bytes, JPEG格式图片的字节数组
    """
    if len(x_values) != len(y_values):
        raise ValueError("x_values和y_values的长度必须一致")

    if sortByX:
        # 结合x和y进行排序
        sorted_pairs = sorted(zip(x_values, y_values))
        x_values, y_values = zip(*sorted_pairs)

    # 创建图表，并设置图表的尺寸
    plt.figure(figsize=(width, height))
    if connect_points:
        plt.plot(x_values, y_values, 'o-')  # 'o-' 表示点和线连接在一起
    else:
        plt.plot(x_values, y_values, 'o')  # 'o' 表示只有点没有线

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(x_values)
    plt.title(title)
    plt.grid(True)

    # 将图表保存到字节数组中
    buf = io.BytesIO()
    plt.savefig(buf, format='jpg')
    buf.seek(0)
    plt.close()

    # 使用Pillow打开图像并保存为JPEG格式字节数据
    img = Image.open(buf)
    byte_array = io.BytesIO()
    img.save(byte_array, format='JPEG')
    byte_array.seek(0)

    if savefilepath == None:
        return byte_array.getvalue()
    else:
        with open(savefilepath, 'wb') as f:
            f.write(byte_array.getvalue())    

if __name__ == "__main__":
    # 示例数据
    x = [1.0, 2.5, 3.7, 5.0, 7.2]
    y = [10, 15, 12, 18, 20]

    # 调用函数作图并获取JPEG图片的字节数组
    jpg_bytes = XY(x, y, connect_points=True, width=10, height=8)

    # 可以将字节数组写入文件以验证
    with open('plot.jpg', 'wb') as f:
        f.write(jpg_bytes)