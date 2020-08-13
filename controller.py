from routing import Route


class Controller:

    @staticmethod
    def index_post(req, msg_assoc = {}):
        print("[SERVER] message recieved: ", msg_assoc)
        return Route.view(req.path.strip("/") + ".html")

    @staticmethod
    def index_get(req, msg_assoc = {}):
        return Route.view(req.path.strip("/") + ".html")