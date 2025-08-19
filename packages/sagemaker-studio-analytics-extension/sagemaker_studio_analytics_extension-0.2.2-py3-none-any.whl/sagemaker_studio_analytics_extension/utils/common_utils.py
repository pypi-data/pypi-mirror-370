def _run_preset_cell_magics(ipy):
    # To allow retry on user errors without kernel restart
    allow_retry_fatal = ipy.find_cell_magic("_do_not_call_allow_retry_fatal")
    allow_retry_fatal("")
    # To delete existing sessions before creating a new one for eac astra connect
    # This is to prevent any race conditions that may arise because of session reuse
    delete_session_magic = ipy.find_cell_magic("_do_not_call_delete_session")
    delete_session_magic("")
