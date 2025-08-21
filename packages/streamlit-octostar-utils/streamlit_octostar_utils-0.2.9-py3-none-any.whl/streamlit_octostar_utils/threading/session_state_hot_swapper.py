from contextlib import contextmanager
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
import streamlit.runtime.state.session_state_proxy as session_state_proxy
import threading


@contextmanager
def SessionStateHotSwapper(context):
    prev_ctx = None
    try:
        with context.session_state._lock:
            thread = threading.current_thread()
            prev_ctx = get_script_run_ctx(suppress_warning=True)
            # docs say this should only be run before the thread starts, but
            # the function only sets an attribute on the thread, should be ok
            add_script_run_ctx(thread, context)
            session_state = session_state_proxy.SessionStateProxy()
            yield session_state
    finally:
        add_script_run_ctx(thread, prev_ctx)
