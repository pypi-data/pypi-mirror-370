# KanvasObjectKlick

KanvasObjectKlick allows you to visualize objects with html on a 2D canvas with the desired color, caption (on hover), and image of the object (on click).

# Installation

```bash
python3 -m pip install --upgrade pip
pip3 install KanvasObjectKlick
```

# Usage

```python
import random
from KanvasObjectKlick import KOKEntity, build_a


keks = []
for i in range(random.randint(3, 50)):
    # name/description of object. It will be displayed when the mouse cursor is hovered over.
    name_i = f"name_{i}"
    
    # x and y, can be float and any range
    coords_i = (random.randint(-1000, 1000)+random.random(), random.randint(-1000, 1000)+random.random())  
    
    # RGB color
    color_i = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))  
    
    # instead of None you can use Pillow, OpenCV image or just path to picture file
    img_i = None  
    
    # Just create KOKEntity
    kok = KOKEntity(name=name_i, coords=coords_i, color=color_i, img=img_i)
    
    keks.append(kok)

# It will create `/path/to/out/file.html` file. Just open it in your browser.
build_a(keks, "/path/to/out/file", zip_need=False)
```

You can also create zip file with `zip_need=True`. In this case, file `/path/to/out/file.zip` will be created.

Instead `build_a` you can use `build_b` (`from KanvasObjectKlick import build_b`). It will create zip with no all in one file. This can be useful when there are too many objects (or rather their images).

```python
# ...

from KanvasObjectKlick import build_b

# It will create `/path/to/out/file.zip` file. Just extract it and open `index.html` in your browser.
build_b(keks, "/path/to/out/file", "/path/to/working/dir")
```

`/path/to/working/dir` can be any directory. It is needed in order to stack temporary files while working. In the end, there will be no garbage left, everything superfluous will be removed.
