from flask import Blueprint, current_app

js_routes_bp = Blueprint('js_routes', __name__)

@js_routes_bp.route("/static/assets/js/jquery.js")
def jquery():
    return current_app.send_static_file("assets/js/jquery.js")

@js_routes_bp.route("/static/assets/js/request.js")
def requestFlask():
    return current_app.send_static_file("assets/js/request.js")


@js_routes_bp.route("/static/vendor/apexcharts/apexcharts-bundle/dist/apexcharts.min.js")
def apexcharts():
    return current_app.send_static_file("vendor/apexcharts/apexcharts-bundle/dist/apexcharts.min.js")

@js_routes_bp.route("/static/vendor/Booststrap/bootstrap.min.js")
def bootstrap():
    return current_app.send_static_file("vendor/Booststrap/bootstrap.min.js")

@js_routes_bp.route("/static/assets/js/home.js")
def home():
    return current_app.send_static_file("assets/js/home.js")

@js_routes_bp.route("/static/assets/js/script.js")
def script():
    return current_app.send_static_file("assets/js/script.js")


@js_routes_bp.route("/static/assets/js/teclado.js")
def teclado():
    return current_app.send_static_file("assets/js/teclado.js")

@js_routes_bp.route("/static/assets/js/vendas.js")
def vendas():
    return current_app.send_static_file("assets/js/vendas.js")
    
@js_routes_bp.route("/static/assets/js/revenda.js")
def revenda():
    return current_app.send_static_file("assets/js/revenda.js")