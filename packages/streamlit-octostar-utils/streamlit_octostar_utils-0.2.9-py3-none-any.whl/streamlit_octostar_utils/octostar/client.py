from octostar.client import make_client, UserContext, User
from functools import wraps
from octostar_streamlit.desktop import whoami
from streamlit.runtime.scriptrunner import get_script_run_ctx
import hashlib
import streamlit as st
import time


def impersonating_running_user(**client_kwargs):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            client = as_running_user(**client_kwargs).user.client
            kwargs["client"] = client
            return func(*args, **kwargs)

        return wrapper

    return decorator


def as_running_user(force_refresh=False):
    session = st.session_state.setdefault("__run_user", {})
    script_ctx = get_script_run_ctx()
    current_time = time.time()

    should_refresh = (
        force_refresh
        or script_ctx.script_requests is not session.get("prev_run")
        or current_time > session.get("token_expiry", 0) - 300  # 5 minutes buffer
    )

    if not should_refresh and "prev_user" in session:
        return UserContext(session["prev_user"])

    running_user = whoami()
    if not running_user:
        return (
            UserContext(session.get("prev_user"))
            if "prev_user" in session
            else st.stop()
        )

    user_hash = int(hashlib.md5(running_user.os_jwt.encode("utf-8")).hexdigest(), 16)
    if "prev_user" not in session or hash(session["prev_user"]) != user_hash:
        client = make_client(fixed_jwt=running_user.os_jwt)
        user = User(client)
        session["prev_user"] = user
        session["token_expiry"] = user.jwt_expires_at

    session["prev_run"] = script_ctx.script_requests
    return UserContext(session["prev_user"])
