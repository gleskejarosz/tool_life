from datetime import datetime

TODAY = datetime.today().strftime('%d-%m-%Y')


def minutes_recalculate(parts, job):
    target = job.target
    minutes = (parts / target) * 60
    return minutes
