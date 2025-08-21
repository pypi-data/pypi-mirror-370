from __future__ import annotations

from flask import Flask, Blueprint
from flask import request
import flask
from flask import abort, redirect
from flask import render_template, send_file

from .. import Random
from ..Thread import Thread
from .. import Lg
from .. import String

#print("load " + '/'.join(__file__.split('/')[-2:]))

import logging 
    
class LoggingMiddleware(object):
    def __init__(self, app):
        self._app = app

    def __call__(self, env, resp):
        errorlog = env['wsgi.errors']
        Lg.Trace('REQUEST', env)

        def log_response(status, headers, *args):
            Lg.Trace('RESPONSE', status, headers)
            return resp(status, headers, *args)

        return self._app(env, log_response)

class Response():
    def Body(self, body:str, statusCode:int=200, contentType:str=None, headers:dict=None) -> flask.Response:
        resp = flask.Response(response=body, status=statusCode, content_type=contentType)
        if headers != None:
            for k in headers:
                resp.headers[str(k)] = str(headers[k])
        return resp
    
    def Status(self, statusCode:int, body:str=None, contentType:str=None, headers:dict=None) -> flask.Response:
        resp = flask.Response(response=body, status=statusCode, content_type=contentType)
        if headers != None:
            for k in headers:
                resp.headers[str(k)] = str(headers[k])
        return resp

    def Redirect(self, location:str, code:int=302) -> flask.Response:
        return redirect(location, code)
    
    def SendFile(self, fpath:str) -> flask.Response:
        return send_file(fpath)

    Abort = abort
    Render = render_template

class RequestArgs():
    def Get(self, name:str, default:str="") -> str | None:
        return request.args.get(name, default)

class RequestForm():
    def Get(self, name:str, default:str="") -> str | None:
        return request.form.get(name, default)

class Request():
    Args = RequestArgs()
    Form = RequestForm()

    @property
    def Headers(self) -> dict[str, str]:
        return dict(request.headers)

    @property
    def Method(self) -> str:
        return request.method

    def Json(self, force:bool=True) -> dict | list:
        return request.get_json(force=force)
    
    @property
    def Data(self, encoding:str="utf-8") -> str:
        return request.get_data().decode(encoding)

    @property
    def DataBytes(self) -> bytes:
        return request.get_data()

class Prefix():
    def __init__(self, webserver:WebServer, path:str) -> None:
        self.webserver = webserver
        self.path = path 
        self.Route = self.webserver.blueprints[self.path].route

class WebServer():
    def __init__(self, debug:bool=True, additionDebug:bool=False, name:str=None):
        """
        It creates a Flask app with a random name.
        
        :param debug: If set to True, the server will reload itself on code changes and provide a
        helpful debugger in case of application errors, defaults to True
        :type debug: bool (optional)
        :param additionDebug: This will print out the request and response headers, defaults to False
        :type additionDebug: bool (optional)
        :param name: The name of the Flask app
        :type name: str
        """
        if not name:
            name = Random.String()

        self.app = Flask(name)
        self.Route = self.app.route 
        self.Request = Request()
        self.Response = Response()
        self.BeforeRequest = self.app.before_request
        self.AfterRequest = self.app.after_request

        if debug == False:
            log = logging.getLogger('werkzeug')
            log.disabled = True
        
        if additionDebug:
            self.app.wsgi_app = LoggingMiddleware(self.app.wsgi_app)
        
        self.blueprints:dict[str, Blueprint] = {}
    
    def Prefix(self, path:str) -> Prefix:
        blueprint = Blueprint(String(path).Filter(), __name__)
        self.blueprints[path] = blueprint

        # self.app.register_blueprint(blueprint, url_prefix=path) # 注册之后再添加的url路由是不生效的

        prefix = Prefix(self, path)
        return prefix
        
    def Run(self, host:str="0.0.0.0", port:int=None, block:bool=True, sslkeyfile:str=None, sslcrtfile:str=None):
        """
        Runs the Flask app on the specified host and port, optionally in a separate thread
        If block is False then debug will always be False
        
        :param host: The hostname to listen on. Set this to '0.0.0.0' to have the server available
        externally as well. Defaults to '127.0.0.1' or 'localhost'
        :type host: str
        :param port: The port to run the server on
        :type port: int
        :param block: If True, the server will run in the main thread. If False, it will run in a
        separate thread, defaults to True
        :type block: bool (optional)
        """

        for path in self.blueprints:
            self.app.register_blueprint(self.blueprints[path], url_prefix=path)

        if not port:
            port = Random.Int(10000, 60000)
        
        ssl_context = None if sslkeyfile == None else (sslcrtfile, sslkeyfile)

        if block:
            self.app.run(host, port, False, ssl_context=ssl_context)
        else:
            Thread(self.app.run, host, port, False, ssl_context=ssl_context)

if __name__ == "__main__":
    w = WebServer()

    @w.Route("/")
    def index():
        return "Hello World!"

    @w.Route("/json")
    def json():
        return {"key": "value"}

    @w.Route("/param/<pname>")
    def param(pname):
        return pname

    @w.Route('/method', methods=['GET', 'POST'])
    def login():
        return w.Request.Method()

    # curl 'http://localhost:8080/getArg?key=value'
    @w.Route("/getArg")
    def getArg():
        return w.Request.Args.Get("key", "")

    # curl -XPOST -F "key=value" http://localhost:8080/form
    @w.Route("/form", methods=["POST"])
    def postForm():
        return w.Request.Form.Get("key")

    # curl -XPOST -d '{"key":"value"}' http://localhost:8080/postjson
    @w.Route("/postjson", methods=["POST"])
    def postJson():
        return w.Request.Json()

    # curl -XPOST -d 'Hello World!' http://localhost:8080/postData
    @w.Route("/postData", methods=["POST"])
    def postData():
        return w.Request.Data()

    w.Run("0.0.0.0", 8080, block=False)

    w2 = WebServer()

    @w2.Route("/")
    def index2():
        # print(w.Request.Headers())
        return "Hello World 2!" 
    
    prefix = w2.Prefix("/a/test/prefix")

    @prefix.Route("suffix")
    def prefix():
        return "prefix"
    
    prefix = w2.Prefix("/prefix")

    @prefix.Route("/suffix") # /prefix/suffix
    def suffix():
        return "suffix"
    
    @w2.BeforeRequest
    def beforereq():
        Lg.Trace("before request")
        # return "200 OK" # 返回非None的值则直接返回这个response给client, 不再执行之后的handler
        return None # 返回None则执行之后的handler
        
    @w2.AfterRequest
    def afterreq(response): # 其他handler返回的response
        Lg.Trace("after request:", response)
        return response # 一定要回一个response, 否则报错500
    
    @w2.Route('/<path:path>', methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"])
    def catch_all(path):
        return f'捕获的路径: {path}, 请求方法: {request.method}', 200
        
    w2.Run("0.0.0.0", 8081) # Block here