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
def addHandler(app,name=None):
    name = name or os.path.splitext(os.path.abspath(__file__))[0]
    audit_handler = logging.FileHandler("{name}.log")
    audit_fmt     = RequestFormatter(
        "%(asctime)s %(remote_addr)s %(user)s %(message)s"
    )
    audit_handler.setFormatter(audit_fmt)
    app.logger.addHandler(audit_handler)
    
    @app.before_request
    def record_ip_for_authenticated_user():
        if hasattr(request, 'user') and request.user:
            # your get_user_by_username gives you .id
            user = get_user_by_username(request.user["username"])
            if user:
                log_user_ip(user["id"], request.remote_addr)
    @app.route("/api/endpoints", methods=["POST"])
    @app.route("/api/endpoints", methods=["GET"])
    def get_endpoints():
        import sys, os, importlib
        endpoints=[]
        for rule in app.url_map.iter_rules():
            
            # skip dynamic parameters if desired, include all
            methods = sorted(rule.methods - {"HEAD", "OPTIONS"})
            endpoints.append((rule.rule, ", ".join(methods)))
        rules = sorted(endpoints, key=lambda x: x[0])
        try:

            return jsonify(rules), 200
        finally:
            sys.path.pop(0)
    return app
