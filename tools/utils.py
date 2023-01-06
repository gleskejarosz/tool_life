
def minutes_recalculate(parts, job):
    target = job.target
    minutes = (parts / target) * 60
    return minutes
