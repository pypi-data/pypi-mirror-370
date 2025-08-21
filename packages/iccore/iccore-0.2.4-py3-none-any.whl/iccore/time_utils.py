import datetime


def get_timestamp_for_paths(input_time: datetime.datetime | None = None):

    if input_time:
        working_time = input_time
    else:
        working_time = datetime.datetime.now()
    return working_time.strftime("%Y%m%dT%H_%M_%S")
