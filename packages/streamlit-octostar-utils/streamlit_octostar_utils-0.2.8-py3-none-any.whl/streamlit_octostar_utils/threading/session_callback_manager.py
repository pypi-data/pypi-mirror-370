import threading
import time
import streamlit as st
import uuid
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit.runtime import get_instance as get_runtime_instance

from .session_state_hot_swapper import SessionStateHotSwapper


class SessionCallbackManager(object):
    instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = super().__new__(cls)
            cls.instance.initialized = False
        return cls.instance

    def __init__(self):
        if not self.initialized:
            self.initialized = True
            self.active_sessions = {}
            self.monitoring_thread_active = False
            self.monitoring_thread_lock = threading.Lock()

    @st.cache_resource
    def get_handler():
        if not SessionCallbackManager.instance:
            SessionCallbackManager.instance = SessionCallbackManager()
        return SessionCallbackManager.instance

    def heartbeat(self):
        inactive_sessions = []
        for session_id, session_info in list(self.active_sessions.items()):
            if session_info["runtime"].is_active_session(
                session_id=session_info["context"].session_id
            ):
                heartbeat_fn = session_info.get("on_heartbeat")
                heartbeat_fn(session_info["context"])
            else:
                inactive_sessions.append(session_id)
        for session_id in inactive_sessions:
            self.on_session_end(session_id)

    def monitoring_thread(self):
        while self.monitoring_thread_active:
            self.heartbeat()
            time.sleep(2)

    def start_monitoring(self):
        with self.monitoring_thread_lock:
            if not self.monitoring_thread_active:
                self.monitoring_thread_active = True
                thread = threading.Thread(target=self.monitoring_thread)
                thread.daemon = True
                thread.start()

    def register_session(
        self, on_session_start=None, on_heartbeat=None, on_session_end=None
    ):
        session_id = str(uuid.uuid4())
        ctx = get_script_run_ctx()
        runtime = get_runtime_instance()
        with self.monitoring_thread_lock:
            self.active_sessions[session_id] = {}
            self.active_sessions[session_id]["session_id"] = session_id
            self.active_sessions[session_id]["context"] = ctx
            self.active_sessions[session_id]["runtime"] = runtime
            self.active_sessions[session_id]["on_session_start"] = (
                SessionCallbackManager.callback_wrapper(on_session_start)
            )
            self.active_sessions[session_id]["on_heartbeat"] = (
                SessionCallbackManager.callback_wrapper(on_heartbeat)
            )
            self.active_sessions[session_id]["on_session_end"] = (
                SessionCallbackManager.callback_wrapper(on_session_end)
            )
        self.on_session_start(session_id)
        return session_id

    def callback_wrapper(callback_fn):
        def _callback(st_context):
            if callback_fn:
                with SessionStateHotSwapper(st_context):
                    callback_fn()

        return _callback

    def on_session_start(self, session_id):
        start_fn = self.active_sessions[session_id].get("on_session_start")
        start_fn(self.active_sessions[session_id]["context"])
        self.start_monitoring()

    def on_session_end(self, session_id):
        with self.monitoring_thread_lock:
            if session_id in self.active_sessions:
                end_fn = self.active_sessions[session_id].get("on_session_end")
                end_fn(self.active_sessions[session_id]["context"])
                self.active_sessions[session_id]["context"].session_state._state.clear()
                self.active_sessions.pop(session_id, None)
                if not self.active_sessions:
                    self.monitoring_thread_active = False
