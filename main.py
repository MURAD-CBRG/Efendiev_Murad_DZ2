import json
import os
import sys
import time
from datetime import datetime

import psycopg2


with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r') as f:
    config = json.load(f)


POLL_INTERVAL = int(os.getenv('POLL_INTERVAL', '300'))
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
LOG_FILE = os.getenv('LOG_FILE')


def emit_log(level, message):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]
    line = f"{ts} [{level}] {message}"

    if level == 'INFO':
        print(line, file=sys.stdout, flush=True)
    else:
        print(line, end='', file=sys.stderr, flush=True)

    if LOG_FILE:
        try:
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(line + '\n')
        except Exception as e:
            print(f"{ts} [ERROR] Не удалось записать в LOG_FILE: {e}",
                  file=sys.stderr, flush=True)


def check_db():
    conn = None
    try:
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            dbname=config['dbname'],
            user=DB_USER,
            password=DB_PASSWORD,
            connect_timeout=config['connect_timeout'],
        )
        cur = conn.cursor()
        cur.execute("SELECT version();")
        row = cur.fetchone()
        cur.close()

        if row and row[0]:
            version = row[0]
            if 'PostgreSQL' in version and '18' in version:
                emit_log('INFO', f"OK. Версия БД: {version}")
            else:
                emit_log('INFO', f"НЕ ТИПИЧНЫЙ ответ БД: {version}")
        else:
            emit_log('INFO', f"Пустой ответ на SELECT version(): {row}")
        return True
    except psycopg2.OperationalError as e:
        emit_log('ERROR', f"Не удалось подключиться к БД: {e}")
        return False
    except Exception as e:
        emit_log('ERROR', f"Непредвиденная ошибка: {e}")
        return False
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass


def main():
    emit_log('INFO', f"Heartbeat запущен. Интервал опроса: {POLL_INTERVAL} сек. "
                     f"LOG_FILE={LOG_FILE}")
    while True:
        check_db()
        time.sleep(POLL_INTERVAL)


if __name__ == '__main__':
    main()