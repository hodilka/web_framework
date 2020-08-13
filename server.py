import socket
import sys
from datetime import datetime
from routing import Route
from email.parser import Parser
from functools import lru_cache
from urllib.parse import parse_qs, urlparse
from controller import Controller


MAX_LINE = 64*1024
MAX_HEADERS = 100
STATIC_DIR = '/static'


class Response:
  MAX_LINE = 64*1024
  MAX_HEADERS = 100
  def __init__(self, status, reason, headers=None, body=None):
    self.status = status
    self.reason = reason
    self.headers = headers
    self.body = body
    print(self.headers)

class MyHTTPServer:
  MAX_LINE = 64*1024
  MAX_HEADERS = 100
  def __init__(self, host, port, server_name):
    self._host = host
    self._port = port
    self._server_name = server_name

  def serve_forever(self):
    serv_sock = socket.socket(
      socket.AF_INET,
      socket.SOCK_STREAM,
      proto=0)

    try:
      serv_sock.bind((self._host, self._port))
      serv_sock.listen()

      while True:
        conn, addr = serv_sock.accept()
        try:
          self.serve_client(conn, addr)
        except Exception as e:
          print('Client serving failed', e)
    finally:
      serv_sock.close()


  def serve_client(self, conn, addr):
    now = datetime.now()
    print(f"[{addr}, {now}] Client Arrived! ")
    try:
      req = self.parse_request(conn)
      resp = self.handle_request(req)
      self.send_response(conn, resp)
    except ConnectionResetError:
      conn = None
    if conn:
      conn.close()

  
  def parse_request(self, conn):
    rfile = conn.recv(64*1024)
    
    raws = rfile.split(b"\n")
    method, target, ver = self.parse_request_line(raws)
    headers = self.parse_headers(raws, method)
    host = headers['Host']
    if not host:
      raise Exception('Bad request')
    if host not in (self._host, f'{self._host}:{self._port}'):
      raise Exception('Not found')
    req = Request(method, target, ver, headers, raws)
    return req


  def parse_headers(self, raws, method):
    if method == "GET":
      headers = raws[1:]
    else:
      headers = raws[1:-2]
    corrected_headers = []
    for raw in headers:
      if raw != b'\r' and raw != b'':
        corrected_headers.append(raw.strip(b'\r'))
    del headers
    dict_of_the_headers = {}
    for raw in corrected_headers:
      raw = raw.decode('iso-8859-1')
      if ": " in raw:
        splited_raw = raw.split(": ")
      else:
        splited_raw = raw.split(":")
      dict_of_the_headers[splited_raw[0]] = splited_raw[1]
    return dict_of_the_headers


  def parse_request_line(self, raws):
    if len(raws[0]) > MAX_LINE:
      raise Exception('Request line is too long')
    print(raws[0])
    req_line = str(raws[0], 'iso-8859-1')
    req_line = req_line.rstrip('\r\n')
    req_line = req_line.rstrip('\r')
    words = req_line.split()            # разделяем по пробелу
    if len(words) != 3:                 # и ожидаем ровно 3 части
      raise Exception('Malformed request line')
    
    method, target, ver = words
    if ver != 'HTTP/1.1':
      raise Exception('Unexpected HTTP version')
    return method, target, ver


  def handle_request(self, req):
    image = True
    if req.method in ['get', 'GET', 'Get']:
      for key, header in req.headers.items():
        if 'Accept' in key and 'text/html' in header:
          image = False
      if not image:
        args_assoc = {}
        print("[PATH]", req.query)
        for key, value in req.query.items():
          val = "".join(value)
          args_assoc[key] = val
        print("[PATH@]", args_assoc) 
        try:
          contr = Controller()
          body_of_the_sendback = getattr(contr, req.path.strip("/") + '_get')(req, args_assoc)
          print(body_of_the_sendback)
        except:
          print("\n[SERVER] cant have body of the sendback")
          return Response(404, 'Not found')
        body = body_of_the_sendback['body'].encode('utf-8')
        contentType = 'text/html; charset=utf-8'
        if not body_of_the_sendback['redirect']:
          headers = [('Content-Type', contentType),
                    ('Content-Length', len(body))]
        else:
          headers = [('Content-Type', contentType),
                    ('Content-Length', len(body)),
                    ('Location', body_of_the_sendback['redirect'])]
        return Response(200, 'OK', headers, body)
      else:
        #returning image
        image_path = STATIC_DIR + req.path
        print("\n[IMAGE PATH]", image_path)
        with open(image_path, "rb") as image:
          f = image.read()
          b = bytearray(f)
          print("[IMAGE] bytearray", b)
          headers = [('Content-Type', "image/png"), ('Content-Length', len(f))]
          return Response(200, 'OK', headers, f)
    if req.method in ['Post', 'post', 'POST']:
      msg = req.body
      msg_splitted = msg.split("&")
      msg_assoc = {}
      for raw in msg_splitted:
        raw_splitted = raw.split("=")
        msg_assoc[raw_splitted[0]] = raw_splitted[1]
      try:
        body_of_the_sendback = getattr(Controller, req.path.strip("/") + '_post')(req, msg_assoc)
      except:
        return Response(404, 'Not found')
      body = body_of_the_sendback.encode('utf-8')
      contentType = 'text/html; charset=utf-8'
      headers = [('Content-Type', contentType),
                ('Content-Length', len(body))]
      return Response(200, 'OK', headers, body)


  def send_response(self, conn, resp):
    wfile = conn.makefile('wb')
    status_line = f'HTTP/1.1 {resp.status} {resp.reason}\r\n'
    wfile.write(status_line.encode('iso-8859-1'))

    if resp.headers:
      for (key, value) in resp.headers:
        header_line = f'{key}: {value}\r\n'
        wfile.write(header_line.encode('iso-8859-1'))

    wfile.write(b'\r\n')

    if resp.body:
      wfile.write(resp.body)
    wfile.flush()
    wfile.close()


class Request(object):
  def __init__(self, method, target, ver, headers, raws):
    self.method = method
    self.target = target
    self.version = ver
    self.headers = headers
    self.all_raws = raws
    
  @property
  def path(self):
    return self.url.path

  @property
  @lru_cache(maxsize=None)
  def query(self):
    return parse_qs(self.url.query)

  @property
  @lru_cache(maxsize=None)
  def url(self):
    return urlparse(self.target)

  @property
  def body(self):
    if self.method == 'POST':
      return self.all_raws[-1].decode('iso-8859-1')


if __name__ == '__main__':
  host = sys.argv[1]
  port = int(sys.argv[2])
  name = sys.argv[3]

  serv = MyHTTPServer(host, port, name)
  try:
    serv.serve_forever()
  except KeyboardInterrupt:
    pass