from starlette.routing import Route
from .features import routes as feature_routes
from .specs import routes as spec_routes
from .verify import routes as verify_routes
from .fragments import routes as fragment_routes
from .metrics import routes as metrics_routes

routes = feature_routes + spec_routes + verify_routes + fragment_routes + metrics_routes
