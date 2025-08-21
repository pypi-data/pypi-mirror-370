# python-fluepdot

This is a small collection of functions for interacting with a
[fluepdot](https://fluepdot.readthedocs.io/en/latest/) module.

import Fluepdot class and create an instance with link as the first arg

```python
from fluepdot import Fluepdot

fd = Fluepdot("http://module.local")
```

## Functions


| function    | args                                  | default values                | return type       | description                                                                           |
|-------------|---------------------------------------|-------------------------------|-------------------|---------------------------------------------------------------------------------------|
| _init_      | baseURL: str, width: int, height: int | x=115, y=16                   | fluepdot.Fluepdot | Constructor for Fluepdot class                                                        |
| post_time   |                                       |                               | None              | indefinitly sets the module to display the current time.                              |
| get_size    |                                       |                               | tuple[int, int]   | returns the size of the connected display                                             |
| get_frame   |                                       |                               | str               | returns the current frame stored by the module                                        |
| get_pixel   | x: int, y: int                        | x=0, y=0                      | bool              | returns the state of a single pixel                                                   |
| get_fonts   |                                       |                               | None              | prints a list of fonts installed on the module                                        |
| get_mode    |                                       |                               | fluepdot.Mode     | returns the mode the module is in                                                     |
| post_text   | text: str, x: int, y: int, font: str  | x=0, y=0, font="DejaVuSans12" | requests.Response | posts a text to the module and returns the requests response                          |
| post_frame  | frame: List[List[bool]], center: bool | center=False                  | requests.Response | posts a frame to the module and returns the requests response                         |
| set_pixel   | x: int, y: int                        | x=0, y=0                      | requests.Response | sets a pixel on the display to active and returns the requests response               |
| unset_pixel | x: int, y: int                        | x=0, y=0                      | requests.Response | sets a pixel on thes display to inactive and returns the requests response            |
| set_mode    | mode: fluepdot.Mode                   | mode=Mode.FULL                | requests.Response | sets the module to FULL or DIFFERENTIAL update mode and returns the requests response |