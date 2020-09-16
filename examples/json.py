from src import Api, Filters, ContentTypes
import json

api = Api(80, rate_limit=10)
api.start()

@api.on_request(Filters.method("GET"), Filters.path("json"))
def a(conn, request):
    conn.reply(json.dumps({"a": "b"}), content_type=ContentTypes.json)
