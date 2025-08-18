import json

from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado
import shutil

class DiskSpaceHandler(APIHandler):
    @tornado.web.authenticated
    def get(self):
        total, used, free = shutil.disk_usage('.')
        self.finish(json.dumps({
            "total": total,
            "used": used,
            "free": free
        }))

def setup_handlers(web_app):
    host_pattern = ".*$"

    base_url = web_app.settings["base_url"]
    disk_route = url_path_join(base_url, "booking-extension", "disk")
    handlers = [(disk_route, DiskSpaceHandler)]
    web_app.add_handlers(host_pattern, handlers)
