"""Build a dependency-free, offline Mars atlas from NASA Mars Trek rasters."""
import argparse
import base64
import gzip
import io
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlencode
from urllib.request import urlopen, Request
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://trek.nasa.gov/mars/trekarcgis/rest/services/'
COLOR = 'Mars_Viking_MDIM21_ClrMosaic_global_232m'
HEIGHT = 'mola128_mola64_merge_90Nto90S_SimpleC_clon0'

def mosaic(service, width, elevation=False):
    tile = min(2048, width // 2)
    height = width // 2
    cols, rows = width // tile, height // tile
    cache = ROOT / '.cache' / f'{service}-{width}'
    cache.mkdir(parents=True, exist_ok=True)
    def get(pos):
        x, y = pos
        path = cache / f'{x}-{y}.{"tif" if elevation else "jpg"}'
        if not path.exists():
            bbox = (-180+360*x/cols, 90-180*(y+1)/rows, -180+360*(x+1)/cols, 90-180*y/rows)
            params = dict(bbox=','.join(map(str,bbox)), size=f'{tile},{tile}', format='tiff' if elevation else 'jpg',pixelType='S16' if elevation else 'U8',interpolation='RSP_BilinearInterpolation',compressionQuality=95,f='image')
            url = BASE + service + '/ImageServer/exportImage?' + urlencode(params)
            with urlopen(Request(url, headers={'User-Agent':'MarsAtlas/1.0'}), timeout=100) as r:
                data = r.read()
            with Image.open(io.BytesIO(data)) as im:
                assert im.size == (tile,tile), (url,im.size)
                if elevation: assert np.asarray(im).dtype.kind in 'iu' and np.asarray(im).dtype.itemsize >= 2
            path.write_bytes(data)
        print(service,x,y,flush=True)
        with Image.open(path) as im:
            return x,y,np.array(im if elevation else im.convert('RGB'))
    out = np.empty((height,width) if elevation else (height,width,3), dtype=np.int32 if elevation else np.uint8)
    with ThreadPoolExecutor(max_workers=3) as pool:
        for x,y,arr in pool.map(get,[(x,y) for y in range(rows) for x in range(cols)]):
            out[y*tile:(y+1)*tile,x*tile:(x+1)*tile] = arr
    return out

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--color',type=int,default=16384,choices=[2048,4096,8192,16384])
    parser.add_argument('--height',type=int,default=8192,choices=[2048,4096,8192,16384])
    args=parser.parse_args()
    assets=ROOT/'assets'; assets.mkdir(exist_ok=True)
    c=assets/f'viking-{args.color}.jpg'; h=assets/f'mola-{args.height}.delta16.gz'
    if not c.exists(): Image.fromarray(mosaic(COLOR,args.color)).save(c,quality=85,subsampling=2)
    if not h.exists():
        arr=mosaic(HEIGHT,args.height,True)
        assert arr.min() >= -12000 and arr.max() <= 30000, (arr.min(),arr.max())
        v=(arr+12000).astype('<u2'); v[:,1:]=v[:,1:]-v[:,:-1]
        h.write_bytes(gzip.compress(v.tobytes(),compresslevel=6,mtime=0))
    template=(ROOT/'src/viewer.html').read_text()
    html=template.replace('__COLOR__','data:image/jpeg;base64,'+base64.b64encode(c.read_bytes()).decode()).replace('__HEIGHT__','data:application/gzip;base64,'+base64.b64encode(h.read_bytes()).decode()).replace('__CW__',str(args.color)).replace('__HW__',str(args.height))
    (ROOT/'index.html').write_text(html)
    print('Standalone size:',len(html)/1024**2,'MiB')

if __name__=='__main__': main()
