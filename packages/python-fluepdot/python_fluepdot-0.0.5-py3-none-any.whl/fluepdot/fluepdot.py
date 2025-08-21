"""
  Small library to interact with a fluepdot controlled display
  https://fluepdot.readthedocs.io/en/latest/

  it should only be required to change the baseURL

  Currently there is no support for changing the timings.
"""

import requests
from requests import Response
from enum import Enum
from typing import Any, Dict, Optional, List

GetParam = Dict[str, Any]
PostParam = str


class Mode(Enum):
    FULL = 0
    DIFFERENTIAL = 1


# endpoints:
frameURL: str = "/framebuffer"
pixelURL: str = "/pixel"
textURL: str = "/framebuffer/text"
fontURL: str = "/fonts"
modeURL: str = "/rendering/mode"


class Fluepdot:
    def __init__(self, baseURL: str, width: int = 115, height: int = 16):
        self.baseURL = baseURL
        self.width = width
        self.height = height
        self.fonts: Optional[List[str]] = None

    def set_url(self, url: str):
        self.baseURL = url

    def post_time(self) -> None:
        import datetime
        dt: str = ""
        while True:
            ndt: str = datetime.datetime.now().strftime("%d.%m.%y %H:%M")
            if ndt != dt:
                dt = ndt
                self.post_text(dt, x=8, y=1, font="fixed_7x14")

    def get_size(self) -> tuple[int, int]:
        frame = self.get_frame()
        self.width = len(frame[0])
        self.height = len(frame) - 1
        return self.width, self.height

    def get_frame(self) -> List[str]:
        r = self._get(frameURL)
        return r.text.split('\n')

    def get_pixel(self, x: int = 0, y: int = 0) -> bool | None:
        r = self._get(pixelURL, get={"x": x, "y": y})
        rtn = True if r.text == "X" else False if r.text == " " else None
        return rtn

    def get_fonts(self) -> None:
        r = self._get(fontURL)
        fonts = r.text.split("\n")
        print(fonts)

    def get_mode(self) -> Mode:
        r = self._get(modeURL)
        return Mode(int(r.text))

    def post_text(self, text: str, x: int = 0, y: int = 0, font: str = "DejaVuSans12") -> Response:
        return self._post(textURL, get={"x": x, "y": y, "font": font}, post=text)

    def post_frame_raw(self, frame: str) -> Response:
        return self._post(frameURL, post=frame)

    def post_frame(self, frame: List[List[bool]], center: bool = False) -> Response:
        data: List[List[str]] = [[" "] * self.width for _ in range(self.height)]
        x_offset: int = 0
        y_offset: int = 0
        if center:
            x_offset = (self.width - max(len(line) for line in frame)) // 2
            y_offset = (self.height - len(frame))//2
        for y, l in enumerate(frame):
            for x, b in enumerate(l):
                if b:
                    try:
                        data[y+y_offset][x+x_offset] = "X"
                    except IndexError as e:
                        print(e)
        outStr = ""
        for line in data:
            outStr = outStr + "".join(line) + "\n"
        return self._post(frameURL, post=outStr)

    def set_pixel(self, x: int = 0, y: int = 0) -> Response:
        return self._post(pixelURL, get={"x": x, "y": y})

    def unset_pixel(self, x: int = 0, y: int = 0) -> Response:
        return self._delete(pixelURL, get={"x": x, "y": y})

    def set_mode(self, mode: Mode = Mode.FULL) -> Response:
        return self._put(modeURL, post=str(mode.value))

    def _delete(self, endpoint: str, get: GetParam | None = None) -> Response:
        if get is None:
            get = {}
        if self.baseURL is None:
            raise RuntimeError('baseURL is None, call set_url')
        return requests.delete(url=self.baseURL + endpoint, params=get)

    def _post(self, endpoint: str, get: GetParam | None = None, post: PostParam = '') -> Response:
        if get is None:
            get = {}
        if self.baseURL is None:
            raise RuntimeError('baseURL is None, call set_url')
        return requests.post(url=self.baseURL + endpoint, params=get, data=post)

    def _put(self, endpoint: str, get: GetParam | None = None, post: PostParam = '') -> Response:
        if get is None:
            get = {}
        if self.baseURL is None:
            raise RuntimeError('baseURL is None, call set_url')
        return requests.put(url=self.baseURL + endpoint, params=get, data=post)

    def _get(self, endpoint: str, get: GetParam | None = None) -> Response:
        if get is None:
            get = {}
        if self.baseURL is None:
            raise RuntimeError('baseURL is None, call set_url')
        return requests.get(url=self.baseURL + endpoint, params=get)


if __name__ == "__main__":
    pass
