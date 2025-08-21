# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function:  pip install python-dotenv
import time
import shutil
import traceback
import multiprocessing
import datetime as dt
from datetime import datetime
from loguru import logger
from dotenv import dotenv_values
from configure import LogDir


config_env = dotenv_values(".env.dev")

gunicorn_dir = LogDir.joinpath("gunicorn")
if not gunicorn_dir.exists():
    gunicorn_dir.mkdir(parents=True, exist_ok=True)


bind = "{0}:{1}".format(config_env.get("HOST"), config_env.get("PORT"))
# 进程文件
pidfile = '{0}/gunicorn.pid'.format(gunicorn_dir)
# 进程数
workers = config_env.get("WORKERS")
# 进程名称
proc_name = "zhousf_project"
# 每个进程开启的线程数
threads = multiprocessing.cpu_count() * 2
# 设置后台守护进程
daemon = config_env.get("DAEMON")
# 设置最大并发量
worker_connections = 50
# 超时
timeout = 1800
# 工作模式协程
worker_class = 'uvicorn.workers.UvicornWorker'
# 日志级别
loglevel = 'warning'
# 访问日志格式
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'
# 访问日志文件
accesslog = "{0}/gunicorn_access.log".format(gunicorn_dir)
# 错误日志文件
errorlog = "{0}/gunicorn_error.log".format(gunicorn_dir)


def delete_log_file(keep_day: int = 7):
    logger.success("Start the scheduled task to delete log files")
    log_file = LogDir.joinpath("delete_log_file.txt")
    msg = [datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')]
    delete_count = 0
    # noinspection PyBroadException
    try:
        business_dir = LogDir.joinpath("business")
        if not business_dir.exists():
            msg.append(f"Dir not found: {business_dir}")
            return
        business_dirs = [d for d in LogDir.joinpath("business").iterdir()]
        if len(business_dirs) == 0:
            return
        current_date = datetime.now().date()
        available_date = []
        for date_ in [current_date - dt.timedelta(days=i) for i in range(keep_day)]:
            available_date.append(str(date_).replace("-", "_"))
        for business_dir in business_dirs:
            date_dirs = [d for d in business_dir.iterdir()]
            if len(date_dirs) == 0:
                continue
            for date_dir in date_dirs:
                if date_dir.name in available_date:
                    continue
                msg.append(str(date_dir))
                logger.info("delete log dir: {0}".format(str(date_dir)))
                delete_count += 1
                shutil.rmtree(date_dir, ignore_errors=True)
    except Exception as e:
        msg.append(str(traceback.print_exc()))
    finally:
        logger.info(f"Delete {delete_count} directory in total")
        msg.append(f"Delete {delete_count} directory in total")
        msg.append("\n")
        with log_file.open("a+", encoding="utf-8") as f:
            f.write("\n".join(msg))


def delete_task(keep_day: int = 30):
    from db import db_task
    logger.success("Start the scheduled task to delete tasks")
    log_file = LogDir.joinpath("delete_task.txt")
    msg = [datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')]
    try:
        tasks = db_task.query_all()
        delete_count = 0
        task_ids = []
        if len(tasks) > 0:
            for task_id in tasks.keys():
                task = tasks.get(task_id)
                create_time = task.get("create_time")
                date1 = datetime.fromtimestamp(create_time)
                date2 = datetime.fromtimestamp(time.time())
                delta = (date2 - date1).days
                if delta > keep_day:
                    db_task.delete(task.get("task_id"))
                    delete_count += 1
                    task_ids.append(task.get("task_id"))
        msg.append(f"Delete {delete_count} task in total: {task_ids}")
        logger.info(f"Delete {delete_count} task in total: {task_ids}")
        msg.append("\n")
    except Exception as e:
        msg.append(f"Error: {e}")
    with log_file.open("a+", encoding="utf-8") as f:
        f.write("\n".join(msg))


def when_ready(server):
    logger.success("Gunicorn on ready.")
    from apscheduler.schedulers.background import BackgroundScheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=delete_log_file, trigger='cron', id="delete_log", max_instances=1, hour=1, minute=59, misfire_grace_time=900)
    scheduler.add_job(func=delete_task, trigger='cron', id="delete_task", max_instances=1, hour=1, minute=30, misfire_grace_time=900)
    scheduler.start()
    logger.success("Scheduler on ready.")


def on_exit(server):
    pass

