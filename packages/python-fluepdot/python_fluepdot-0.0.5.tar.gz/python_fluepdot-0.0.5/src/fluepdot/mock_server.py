# mock server for the fluepdot api
from fluepdot import Mode
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import logging
from threading import Thread
import re

# Third-party imports...
import requests

class MockServerRequestHandler(BaseHTTPRequestHandler):
    FRAME_PATTERN = re.compile(r'/framebuffer')
    PIXEL_PATTERN = re.compile(r'/pixel')
    TEXT_PATTERN = re.compile(r'/framebuffer/text')
    FONT_PATTERN = re.compile(r'/fonts')
    MODE_PATTERN = re.compile(r'/rendering/mode')
    TIMEING_PATTERN = re.compile(r'/rendering/timings')

    framebuffer = [115*[False] for _ in range(16)]
    rendermode = Mode.FULL

    def do_GET(self):
        # /framebuffer
        # /pixel x y
        # /fonts
        # /rendering/mode
        # /rendering/timings
        # Process an HTTP GET request and return a response with an HTTP 200 status.
        if re.search(self.FRAME_PATTERN, self.path):
          if re.search(self.TEXT_PATTERN, self.path):
            # invalid endpoint (text does not support get)
            self.send_response(requests.codes.not_found)
            self.end_headers()
          else:
            msg = '/n'.join(''.join('X' if x else ' ' for x in i) for i in self.framebuffer)
            self.send_response(requests.codes.ok)
            self.end_headers()
            self.wfile.write(msg.encode('utf-8'))
        elif re.search(self.PIXEL_PATTERN, self.path):
            query = parse_qs(urlparse(self.path).query)
            try:
                x = int(query['x'][0])
                y = int(query['y'][0])
                msg = 'X' if self.framebuffer[y][x] else ' '
                self.send_response(requests.codes.ok)
                self.end_headers()
                self.wfile.write(msg.encode('utf-8'))
            except Exception:
                logging.debug(' invalid pixel get %s', self.path)
                self.send_response(requests.codes.bad)
                self.end_headers()
        elif re.search(self.FONT_PATTERN, self.path):
            msg = "mock font for fluepdot\nmock_font\nsecond font for mock server\nmock_font2"
            self.send_response(requests.codes.ok)
            self.end_headers()
            self.wfile.write(msg.encode('utf-8'))
        elif re.search(self.MODE_PATTERN, self.path):
            logging.debug(' mode GET endpoint %s', self.path)
            self.send_response(requests.codes.ok)
            self.end_headers()
            self.wfile.write(self.rendermode.value.encode('ascii'))
        else:
            logging.debug(' invalid GET endpoint %s', self.path)
            self.send_response(requests.codes.bad)
            self.end_headers()
        return

    def do_PUT(self):
        # Process an HTTP PUT request and return a response with an HTTP 200 status.
        # /rendering/mode
        if re.search(self.MODE_PATTERN, self.path):
            self.rendermode = Mode(int(self.rfile.read(int(self.headers.get('content-length')))))
            logging.debug(' mode set to %s', self.rendermode)
            self.send_response(requests.codes.ok)
            self.end_headers()
        else:
            logging.debug(' invalid PUT endpoint %s', self.path)
            self.send_response(requests.codes.bad)
            self.end_headers()
        return

    def do_POST(self):
        # Process an HTTP POST request and return a response with an HTTP 200 status.
        # /framebuffer
        # /framebuffer/text p=text g=x,y,font
        # /pixel x y
        # /rendering/timings
        logging.debug(' POST endpoint %s', self.path)
        if re.search(self.FRAME_PATTERN, self.path):
            if re.search(self.TEXT_PATTERN, self.path):
                query = parse_qs(urlparse(self.path).query)
                try:
                    x = int(query['x'][0])
                    y = int(query['y'][0])
                    font = query['font'][0]
                    text = self.rfile.read(int(self.headers.get('content-length'))).decode('utf-8')
                    logging.debug(' text %s at %d,%d with font %s', text, x, y, font)
                    self.send_response(requests.codes.ok)
                    self.end_headers()
                except Exception:
                    logging.debug(' invalid POST endpoint %s', self.path)
                    self.send_response(requests.codes.bad)
                    self.end_headers()
            else:
                logging.debug(' framebuffer endpoint %s', self.path)
                data = self.rfile.read(int(self.headers.get('content-length')))
                logging.debug(' data %s', data)
                self.framebuffer = [[True if x == 'X' else False for x in i] for i in data.decode('utf-8').split('\n')]
                self.send_response(requests.codes.ok)
                self.end_headers()
        elif re.search(self.PIXEL_PATTERN, self.path):
            query = parse_qs(urlparse(self.path).query)
            try:
                x = int(query['x'][0])
                y = int(query['y'][0])
                self.framebuffer[y][x] = True
                logging.debug(' pixel set %s, %s', x, y)
                self.send_response(requests.codes.ok)
                self.end_headers()
            except Exception:
                logging.debug(' invalid pixel set %s', self.path)
                self.send_response(requests.codes.bad)
                self.end_headers()
        elif re.search(self.TIMEING_PATTERN, self.path):
            # TODO: implement this correctly
            print('timing endpoint', self.path)
            self.send_response(requests.codes.unsupported)
            self.end_headers()
        else:
            logging.debug(' invalid POST endpoint %s', self.path)
            self.send_response(requests.codes.bad)
            self.end_headers()
        return

    def do_DELETE(self):
        # Process an HTTP DELETE request and return a response with an HTTP 200 status.
        # /pixel x y
        if re.search(self.PIXEL_PATTERN, self.path):
            query = parse_qs(urlparse(self.path).query)
            try:
                x = int(query['x'][0])
                y = int(query['y'][0])
                self.framebuffer[y][x] = False
                logging.debug(' pixel unset %s, %s', x, y)
                self.send_response(requests.codes.ok)
                self.end_headers()
            except Exception:
                logging.debug(' invalid pixel unset %s', self.path)
                self.send_response(requests.codes.bad)
                self.end_headers()
        else:
            logging.debug(' invalid DELETE endpoint %s', self.path)
            self.send_response(requests.codes.bad)
            self.end_headers()
        return


class TestMockServer(object):
    @classmethod
    def setup_class(cls):
        # Configure mock server.
        cls.mock_server = HTTPServer(('localhost', 8080), MockServerRequestHandler)

        # Start running mock server in a separate thread.
        # Daemon threads automatically shut down when the main process exits.
        cls.mock_server_thread = Thread(target=cls.mock_server.serve_forever, daemon=True)
        cls.mock_server_thread.start()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.debug(' starting mock server')
    server = TestMockServer().setup_class()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        logging.debug(' stopping mock server')
    