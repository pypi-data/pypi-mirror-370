from PIL import Image

#print("load " + __file__.split('/')[-1])

def ResizeImage(src:str, dst:str, width:int, quality:int=95):
    img = Image.open(src)

    w, h = img.size
    # print('Befor resize (w,h): ' + str((w,h)))

    if w > width:
        w  = float(w)
        h = float(h)
        width = float(width)
        if w > h:
            precent = width / h
            w = precent * w
            h = precent * h
        else:
            precent = width / w
            h = precent * h
            w = precent * w
        w = int(w)
        h = int(h)
        # print 'After resize (w,h): ' + str((w,h))
        img = img.resize((w, h), Image.Resampling.LANCZOS)
        # print 'Saving to ' + dst
        
    if dst.lower().endswith(".jpg") or dst.lower().endswith("jpeg"):
        img = img.convert('RGB')
        img.save(dst, "JPEG", quality = quality)
    elif dst.lower().endswith(".png"):
        img.save(dst, "PNG", quality = quality)
    else:
        raise Exception("不支持的导出类型, 支持文件后缀: .jpg, .jpeg, .png")

def ConvertImageFormate(src:str, dst:str, quality:int=95):
    img = Image.open(src)

    if dst.lower().endswith(".jpg") or dst.lower().endswith("jpeg"):
        img = img.convert('RGB')
        img.save(dst, "JPEG", quality = quality)
    elif dst.lower().endswith(".png"):
        img.save(dst, "PNG", quality = quality)
    else:
        raise Exception("不支持的导出类型, 支持文件后缀: .jpg, .jpeg, .png")

if __name__ == "__main__":
    ResizeImage("/Users/darren/Downloads/IMG_2560.JPG", "/Users/darren/Downloads/IMG_2560_Resized.JPG", 1920)
    ResizeImage("/Users/darren/Downloads/IMG_2560.JPG", "/Users/darren/Downloads/IMG_2560_Resized.PNG", 1920)

