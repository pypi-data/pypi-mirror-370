import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import argparse
from r00logger import set_level, log, add_file
from r00tinder.module.session import Session



def reger_start(id_phone=None, log_level=None):
    if id_phone:
        set_level(log_level) if log_level else set_level('TRACE')
        return _reger_start(id_phone)

    p = argparse.ArgumentParser()
    p.add_argument("id_phone")
    p.add_argument("log_level", default='TRACE')
    p.add_argument("log_file", nargs="?")
    a = p.parse_args()

    if a.log_file:
        # пишем ТОЛЬКО в файл, без stdout (чтобы не было дублирования с редиректом шелла)
        add_file(a.log_file, level=a.log_level, replace_stdout=True)
    else:
        # fallback: лог в stdout
        set_level(a.log_level)

    return _reger_start(a.id_phone)


def _reger_start(id_phone):
    session = Session(id_phone)
    log.info(session)
    log.trace(id_phone)
    exit()

    try:
        session.create_new()
    finally:
        session.finish()


if __name__ == '__main__':
    reger_start(14)