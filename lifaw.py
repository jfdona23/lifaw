"""
Lifaw - light and fast web framework
"""
import socket
import types
from json import dumps
from inspect import signature


class Lifaw:
    """Lifaw"""
    __routes = dict()
    allowedMethods = ("GET", "POST")
    for i in allowedMethods:
        __routes[i] = dict()

    def serveApp(self, host, port, debug=False):
        """serveApp"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Needed to reuse a connection avoiding the TIME_WAIT. Please be careful with this.
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen()
        while True:
            conn, addr = s.accept()
            print('Connection received:', addr)
            data = conn.recv(1024)
            if not data:
                continue
            r = self.parseRequest(data)
            method = r["method"]
            route = r["route"]
            if method not in self.allowedMethods or route not in self.__routes[method].keys():
                response = self.buildErrorResponse("Bad Request", 400)
            elif method in ["POST"]:
                response = self.handleRequestWithBody(data)
            else:
                response = self.handleRequest(data)
            conn.sendall(response)
            if debug:
                print("\nREQUEST: \n" + data.decode("utf-8"))
                print("\nRESPONSE: \n" + response.decode("utf-8"))
            conn.close()
        s.close()
        return

    def addRoute(self, route, func, method="GET"):
        """addRoute"""
        if not isinstance(func, types.FunctionType):
            func = self.buildErrorResponse
        self.__routes[method].update({route:func})
        return

    def buildErrorResponse(self, msg="Default Error", statusCode=500):
        """buildErrorResponse"""
        msg = str(msg)  # Ensure message is a string
        msgLength = len(msg)
        h = "HTTP/1.1 %d %s \n \
            Content-Type: text/html \n \
            Content-Length: %d \n \
            Cache-Control: no-cache, private \n \
            User-Agent:M Lifaw/0.1 \n\n" % (statusCode, msg, msgLength)
        h = bytes(h, "utf-8")
        msg = bytes(msg, "utf-8")
        return h + msg

    def buildResponse(self, msg, content="text/html"):
        """buildResponse"""
        if isinstance(msg, dict):
            msg = dumps(msg)
        msgLength = len(msg)
        h = "HTTP/1.1 200 OK \n \
            Content-Type: %s \n \
            Content-Length: %x \n \
            Cache-Control: no-cache, private \n \
            User-Agent:M Lifaw/0.1 \n\n" % (content, msgLength)
        h = bytes(h, "utf-8")
        msg = bytes(msg, "utf-8")
        return h + msg

    def handleRequest(self, data):
        """handleRequest"""
        r = self.parseRequest(data)
        method = r["method"]
        route = r["route"]
        if "parameters" in r.keys():
            params = r["parameters"]
        else:
            params = {"Error": True}
        if len(signature(self.__routes[method][route]).parameters) > 0:
            return self.__routes[method][route](params)
        return self.__routes[method][route]()

    def handleRequestWithBody(self, data):
        """handleRequestWithBody"""
        r = self.parseRequest(data)
        headers = r["headers"]
        body = r["body"]
        ## WORK IN PROGRESS ##
        print(type(headers))
        print(type(body))
        return "WORKINPROGRESS"

    def parseRequest(self, data):
        """parseRequest"""
        data = data.decode("utf-8")
        reqAttributes = dict()
        params = dict()
        if len(data.split("\n\n")) == 2:
            headers, body = data.split("\n\n")
            reqAttributes["body"] = body
        else:
            headers = data
        method, uri, proto= data.split("\n")[0].split()
        if len(uri.split("?")) == 2:
            route, parameters = uri.split("?")
            for p in parameters.split("&"):
                k, v = p.split("=")
                params[k] = v
            reqAttributes["parameters"] = params    # Dict type
        else:
            route = uri
        reqAttributes["protocol"] = proto
        reqAttributes["method"] = method
        reqAttributes["route"] = route
        reqAttributes["headers"] = headers
        return reqAttributes

    def parseJsonBody(self):
        """parseJsonBody"""
        return
     

if __name__ == "__main__":
    pass