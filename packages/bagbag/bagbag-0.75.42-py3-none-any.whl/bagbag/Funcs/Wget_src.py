import os
import urllib.parse as urlparse
import time 
import requests
import tqdm

#print("load " + __file__.split('/')[-1])

def download_file(url, dest):
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        total_size_in_bytes= int(response.headers.get('content-length', 0))
        chunk_size=8192
        progress_bar = tqdm.tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
        with open(dest, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size): 
                progress_bar.update(len(chunk))
                f.write(chunk)
        progress_bar.close()
        print(progress_bar.n, total_size_in_bytes)
        if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
            raise Exception("Download error")

def Wget(url:str, dest:str=None, override=True):
    if dest == None:
        fname = os.path.basename(urlparse.urlparse(url).path)
        if len(fname.strip(" \n\t.")) == 0:
            dest = "wget.downloaded." + str(time.time())
        else:
            dest = fname

    if os.path.exists(dest):
        if override:
            download_file(url, dest)
        else:
            raise Exception(f"目标文件已存在: {dest}")
    else:
        download_file(url, dest)

if __name__ == "__main__":
    Wget("http://mirror.nl.leaseweb.net/speedtest/10000mb.bin", "test.10mb")
    import os
    os.system('rm -rf test.10mb')