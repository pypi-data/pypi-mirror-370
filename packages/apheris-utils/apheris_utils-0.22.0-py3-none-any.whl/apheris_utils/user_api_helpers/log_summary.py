import warnings
from typing import List, Set

N_MESSAGES_PER_SENDER = 3
N_MESSAGES_SERVER = 3


def _get_id_of_message_sender(log_line: str) -> str:
    x = log_line.split("Message from '")
    if len(x) < 2:
        raise RuntimeError("Unexpected message format.")
    y = x[1].split("'")[0]
    if len(y) == 0:
        raise RuntimeError("Unexpected message format.")
    return y


def _is_message(log_line: str) -> bool:
    return "Message from" in log_line


def _get_ids_of_all_message_senders(log: str) -> Set[str]:
    return {_get_id_of_message_sender(x) for x in log.split("\n") if _is_message(x)}


def _is_error(log_line: str) -> bool:
    return ("error" in log_line) or ("ERROR" in log_line)


def _get_error_messages_of_sender(sender: str, log: str) -> List[str]:
    messages = _get_last_messages_of_sender(sender=sender, log=log)
    return [x for x in messages if _is_error(x)]


def _get_last_messages_of_sender(
    sender: str, log: str, n: int | None = None
) -> List[str]:
    messages = [x for x in log.split("\n") if _is_message(x) and (sender in x)]
    if n:
        return messages[-n:]
    else:
        return messages


def _get_server_logs(log: str, n: int | None = None) -> List[str]:
    log_lines = [x for x in log.split("\n") if ((not _is_message(x)) and len(x) > 0)]
    if n:
        return log_lines[-n:]
    else:
        return log_lines


def _get_server_errors(log: str) -> List[str]:
    log_lines = _get_server_logs(log=log)
    return [x for x in log_lines if _is_error(x)]


def create_log_summary(
    log: str,
    n_messages_per_sender: int = 3,
    n_messages_server: int = 3,
) -> str:
    s = "######### SUMMARY OF RELEVANT LOGS #########\n\n"

    try:
        s += "\n# ERROR MESSAGES OF CLIENTS\n"
        for sender in _get_ids_of_all_message_senders(log):
            s += f"\n## sender: {sender}\n\n"
            for message in _get_error_messages_of_sender(sender, log):
                s += message + "\n\n"
    except RuntimeError:
        warnings.warn(
            "Skipped `ERROR MESSAGES OF CLIENTS` section because of malformated logs."
        )

    s += "\n# ERROR MESSAGES OF SERVER\n\n"
    for message in _get_server_errors(log):
        s += message + "\n\n"

    try:
        s += f"# LAST {n_messages_per_sender} MESSAGES OF CLIENTS\n"
        for sender in _get_ids_of_all_message_senders(log):
            s += f"\n## sender: {sender}\n\n"
            for message in _get_last_messages_of_sender(
                sender, log, n_messages_per_sender
            ):
                s += message + "\n\n"
    except RuntimeError:
        warnings.warn(
            "Skipped `LAST MESSAGES OF CLIENTS` section because of malformated logs."
        )

    s += f"\n# LAST {n_messages_server} MESSAGES OF SERVER\n\n"
    for message in _get_server_logs(log=log, n=n_messages_server):
        s += message + "\n\n"

    return s
