
from flask_cors import CORS
from abstract_utilities import make_list,get_media_types,get_logFile,eatAll
from multiprocessing import Process
from flask import *
from abstract_queries import USER_IP_MGR
from .file_utils import *
from .request_utils import *
from .network_utils import *
from werkzeug.utils import secure_filename
import os,sys,unicodedata,hashlib,json,logging
from abstract_security import get_env_value    
logger = get_logFile('abstract_flask')
import uuid
def install_request_ids(app):
    @app.before_request
    def _rid_start():
        rid = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        g.request_id = rid

    @app.after_request
    def _rid_hdr(resp):
        resp.headers["X-Request-ID"] = getattr(g, "request_id", "")
        return resp
from werkzeug.datastructures import Range

def send_media_partial(path, mimetype=None, as_attachment=False, download_name=None):
    # Determine file size
    file_size = os.path.getsize(path)
    # Parse Range
    rng = request.range or Range(None)
    start, end = 0, file_size - 1
    if rng and rng.ranges:
        (start, end) = rng.ranges[0]
        start = 0 if start is None else start
        end   = file_size - 1 if end is None else end
        if start > end or end >= file_size:
            return Response(status=416, headers={"Content-Range": f"bytes */{file_size}"})
        status = 206
        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(end - start + 1),
        }
        with open(path, "rb") as f:
            f.seek(start)
            data = f.read(end - start + 1)
        resp = Response(data, status=status, mimetype=mimetype)
        for k, v in headers.items(): resp.headers[k] = v
        if as_attachment and download_name:
            resp.headers["Content-Disposition"] = f'attachment; filename="{download_name}"'
        return resp
    # No Range → normal full response (304/ETag still applies)
    return send_file(path, mimetype=mimetype, as_attachment=as_attachment,
                     download_name=download_name, conditional=True)
import urllib.parse
def content_disposition(name, attachment=True):
    name = secure_filename(name) or "download"
    quoted = urllib.parse.quote(name)
    disp = "attachment" if attachment else "inline"
    return f"{disp}; filename*=UTF-8''{quoted}"
def install_security_headers(app):
    @app.after_request
    def _sec(resp):
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        resp.headers.setdefault("Referrer-Policy", "no-referrer-when-downgrade")
        # If you serve any HTML from this app, consider CSP (careful with media)
        # resp.headers.setdefault("Content-Security-Policy", "default-src 'self'")
        return resp

def install_openapi(app, title="Media API", version="1.0.0", servers=None):
    servers = servers or [{"url": request.url_root.rstrip("/")}]
    @app.get("/openapi.json")
    def _openapi():
        paths = {}
        for rule in app.url_map.iter_rules():
            if rule.endpoint == "static":  # skip Flask static
                continue
            methods = sorted(m for m in rule.methods if m not in {"HEAD","OPTIONS"})
            paths[rule.rule] = {m.lower(): {"responses": {"200": {"description": "OK"}}} for m in methods}
        return jsonify({"openapi":"3.0.0","info":{"title":title,"version":version},"servers":servers,"paths":paths})

def install_health(app):
    @app.get("/healthz")
    def _healthz(): return jsonify({"ok": True}), 200

    @app.get("/readyz")
    def _readyz():
        # Add quick checks (disk, dir exists, DB ping etc.)
        ok = os.path.isdir(app.config.get("UPLOAD_FOLDER", ""))
        return (jsonify({"ok": ok}), 200 if ok else 503)
def install_method_override(app, allowed=("PATCH","DELETE","PUT")):
    @app.before_request
    def _method_override():
        if request.method == "POST":
            m = request.headers.get("X-HTTP-Method-Override", "").upper()
            if m in allowed:
                request.environ["REQUEST_METHOD"] = m
def install_fast_options(app):
    @app.route("/", defaults={"path": ""}, methods=["OPTIONS"])
    @app.route("/<path:path>", methods=["OPTIONS"])
    def _opts(path):
        resp = app.make_default_options_response()
        # You can add any dynamic logic here; CORS extension will still apply
        return resp
def install_caching_headers(app, max_age_secs=86400):
    @app.after_request
    def _cache(resp):
        # only cache GET/HEAD 2xx for static/media paths
        if request.method in ("GET", "HEAD") and resp.status_code == 200:
            p = request.path
            if p.startswith(app.static_url_path or "/static") or p.startswith("/media"):
                resp.headers.setdefault("Cache-Control", f"public, max-age={max_age_secs}, immutable")
        return resp
def get_from_kwargs(keys,**kwargs):
    output_js = {}
    for key in keys:
        if key in kwargs:
            output_js[key]= kwargs.get(key)
            del kwargs[key]
    return output_js,kwargs
def get_name(name=None,abs_path=None):
    if os.path.isfile(name):
        basename = os.path.basename(name)
        name = os.path.splitext(basename)[0]
    abs_path = abs_path or __name__
    return name,abs_path
def jsonify_it(obj):
    if isinstance(obj,dict):
        status_code = obj.get("status_code")
        return jsonify(obj),status_code
def get_bp(name=None,abs_path=None, **bp_kwargs):
    # if they passed a filename, strip it down to the module name
    name,abs_path = get_name(name=name,abs_path=abs_path)
    bp_name = f"{name}_bp"
    logger  = get_logFile(bp_name)
    logger.info(f"Python path: {sys.path!r}")
    # build up only the kwargs they actually gave us
    bp = Blueprint(
        bp_name,
        abs_path,
        **bp_kwargs,
    )
    return bp, logger
class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            # `request` is the current flask.Request proxy
            ip_addr = get_ip_addr(req=request)
            user = USER_IP_MGR.get_user_by_ip(ip_addr)
            record.remote_addr = ip_addr
            record.user = user
        else:
            record.remote_addr = None
            record.user = None
        return super().format(record)
def get_static_url_ends(endpoint,app):
    static_url= eatAll(app.static_url_path,['/'])
    endpoint= eatAll(endpoint,['/'])
    return f"/{static_url}/{endpoint}",f"/{static_url}/{endpoint}/"
    
def addHandler(app: Flask, *, name: str | None = None) -> Flask:
    # ---- short-circuit if we've already been here ---------
    if getattr(app, "_endpoints_registered", False):
        return app
    app._endpoints_registered = True               # mark as done
    # -------------------------------------------------------

    name = name or os.path.splitext(os.path.basename(__file__))[0]
    
    # ---- audit logger -------------------------------------
    audit_path  = f"{name}.log"
    audit_fmt   = RequestFormatter(
        "%(asctime)s %(remote_addr)s %(user)s %(message)s"
    )
    audit_hdlr  = logging.FileHandler(audit_path)
    audit_hdlr.setFormatter(audit_fmt)
    app.logger.addHandler(audit_hdlr)

    # ---- request hooks ------------------------------------
    @app.before_request
    def record_ip_for_authenticated_user():
        if getattr(request, "user", None):
            user = get_user_by_username(request.user["username"])
            if user:
                log_user_ip(user["id"], request.remote_addr)

    # ---- single, multi-method route -----------------------
    if "getEnds" not in app.view_functions:        # extra belt-and-braces
        static_url= eatAll(app.static_url_path,['/'])
        @app.route(f"/{static_url}/endpoints/", methods=["GET", "POST"])
        def getEnds():
            endpoints = [
                (rule.rule, ", ".join(sorted(rule.methods - {"HEAD", "OPTIONS"})))
                for rule in app.url_map.iter_rules()
            ]
            return jsonify(sorted(endpoints)), 200

    return app
def install_json_errors(app):
    def _json_error(status, message, **kw):
        resp = jsonify({"error": message, "status": status, **kw})
        resp.status_code = status
        return resp

    @app.errorhandler(404)
    def _404(e): return _json_error(404, "Not Found", path=request.path)

    @app.errorhandler(405)
    def _405(e):
        resp = _json_error(405, "Method Not Allowed", path=request.path)
        # copy Allow header so clients can recover
        allow = e.valid_methods if hasattr(e, "valid_methods") else None
        if allow: resp.headers["Allow"] = ", ".join(allow)
        return resp

    @app.errorhandler(413)
    def _413(e): return _json_error(413, "Payload Too Large")

    @app.errorhandler(Exception)
    def _500(e):
        app.logger.exception("Unhandled exception")
        return _json_error(500, "Internal Server Error")

def install_trailing_slash_policy(app, *, canonical="no-trailing"):
    """
    canonical: "no-trailing" -> redirect '/path/'  -> '/path'
               "trailing"    -> redirect '/path'   -> '/path/'
               None          -> do nothing
    """
    if canonical not in ("no-trailing", "trailing", None):
        raise ValueError("canonical must be 'no-trailing', 'trailing', or None")

    # Make Flask tolerant first (no 308s if already exact match)
    app.url_map.strict_slashes = False
    # Optional: collapse duplicate slashes (// -> /) if supported
    try:
        app.url_map.merge_slashes = True
    except Exception:
        pass

    if canonical is None:
        return

    @app.before_request
    def _normalize_slash():
        p = request.path
        if p == "/":
            return  # never touch root

        want_trailing = (canonical == "trailing")
        has_trailing = p.endswith("/")

        if want_trailing and not has_trailing:
            target = p + "/"
        elif (not want_trailing) and has_trailing:
            target = p.rstrip("/")
        else:
            return  # already canonical

        qs = ("?" + request.query_string.decode()) if request.query_string else ""
        # 308 preserves method + body (safer for APIs than 301/302)
        return redirect(target + qs, code=308)

    @app.after_request
    def _add_canonical_header(resp):
        # Optional: advertise your canonical policy to clients/tools
        resp.headers["X-Trailing-Slash-Policy"] = canonical
        return resp

def register_bps(app,bp_list):
    for bp in bp_list:
        app.register_blueprint(bp)
    return app
def get_Flask_app(*args,**kwargs):
    """Quart app factory."""
    keys = ['name','bp_list']
    values , kwargs = get_from_kwargs(keys,**kwargs)
    name = values.get('name')
    bp_list = values.get('bp_list')
    for arg in args:
        if not name and not isinstance(arg,list):
            name = arg
        elif not bp_list:
            bp_list = arg
    bp_list = bp_list or []
    name,abs_path = get_name(name)
    app = Flask(name,**kwargs)
    app = addHandler(app,name=name)
    app = register_bps(app,bp_list)
    return app
def main_flask_start(app, key_head: str = '', env_path=None, **kwargs):
    key_head = (key_head or '').upper()
    KEY_VALUS = {
        "DEBUG": {"type": bool, "default": True},
        "HOST":  {"type": str,  "default": '0.0.0.0'},
        "PORT":  {"type": int,  "default": 5000},
    }
    for key, spec in KEY_VALUS.items():  # fixed .items()
        env_key = f"{key_head}_{key}" if key_head else key
        raw = get_env_value(path=env_path, key=env_key)
        if raw is None:
            KEY_VALUS[key] = spec["default"]
        else:
            t = spec["type"]
            KEY_VALUS[key] = (raw if t is str else (raw.lower() in ("1", "true", "yes") if t is bool else t(raw)))
    app.run(debug=KEY_VALUS["DEBUG"], host=KEY_VALUS["HOST"], port=KEY_VALUS["PORT"])
