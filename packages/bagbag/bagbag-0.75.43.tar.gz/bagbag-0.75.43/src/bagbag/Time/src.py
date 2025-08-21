#print("load time")

def FormatDuration(seconds:int) -> str:
    import datetime
    
    # 使用 timedelta 来计算时间间隔
    time_delta = datetime.timedelta(seconds=seconds)
    # 计算年、月、周、天、小时、分钟和秒
    years = time_delta.days // 365
    months = (time_delta.days % 365) // 30
    weeks = (time_delta.days % 365 % 30) // 7
    days = time_delta.days % 365 % 30 % 7
    hours, remainder = divmod(time_delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    # 构建人类可读的时间字符串
    time_string = ""
    if years > 0:
        time_string += "{} years, ".format(years)
    if months > 0:
        time_string += "{} months, ".format(months)
    if weeks > 0:
        time_string += "{} weeks, ".format(weeks)
    if days > 0:
        time_string += "{} days, ".format(days)
    time_string += "{:02}:{:02}:{:02}".format(hours, minutes, seconds)
    return time_string

def Now() -> float:
    import time

    return time.time()

def NowString(format:str="%Y-%m-%d %H:%M:%S", utc:bool=False) -> str:
    import time
    import datetime
    import pytz

    dobj = datetime.datetime.fromtimestamp(time.time())
    if utc == True:
        dobj = dobj.astimezone(pytz.utc)
    return dobj.strftime(format)

def Sleep(num:int=0, title:str=None, bar:bool=None):
    """
    Sleep(num:int, bar:bool=None)
    
    The first argument is an integer, and the second argument is a boolean. The second argument is
    optional, and if it is not provided, it will be set to True if the first argument is greater than 5,
    and False otherwise
    
    :param num: The number of seconds to sleep
    :type num: int
    :param bar: If True, a progress bar will be displayed. If False, no progress bar will be displayed.
    If None, a progress bar will be displayed if the number of seconds is greater than 5
    :type bar: bool
    """

    import time

    if num == 0:
        while True:
            time.sleep(333)
    else:
        if bar == None:
            if num > 5:
                bar = True 
            else:
                bar = False

        if bar:
            import tqdm

            num = int(num)
            for _ in tqdm.tqdm(range(num), total=num, leave=False, desc=title):
                time.sleep(1)
        else:
            time.sleep(num)

def Strftime(timestamp:float|int, format:str="%Y-%m-%d %H:%M:%S", utc:bool=False) -> str:
    """
    It converts a timestamp to a string.
    
    :param format: The format string to use
    :type format: str
    :param timestamp: The timestamp to format
    :type timestamp: float|int
    :return: A string
    """
    import datetime
    import pytz

    dobj = datetime.datetime.fromtimestamp(timestamp)
    if utc == True:
        dobj = dobj.astimezone(pytz.utc)
    return dobj.strftime(format)

def parseTimeago(timestring:str) -> int|None:
    from ..String import String

    if timestring == "just now":
        return int(Now())
    
    res = String(timestring).RegexFind('([0-9]+)([smhdw])')
    # print(res)
    if len(res) != 0:
        sm = {
            "s": "second",
            "m": "minute",
            "h": "hour",
            "d": "day",
            "w": "week",
        }
        timestring = res[0][1] + " " + sm[res[0][2]] + " ago"

    formates = [
        "([0-9]+) %ss{0,1} ago",
        "in ([0-9]+) %ss{0,1}",
        "([0-9]+) %s\. ago"
    ]

    step = {
        "second": 1,
        "minute": 60,
        "hour": 3600,
        "day": 86400,
        "week": 604800,
        "month": 2592000,
        "mo": 2592000,
        "year": 31536000,
        "yr": 31536000,
    }

    for s in step:
        for f in formates:
            f = f % s 

            res = String(timestring).RegexFind(f)
            if len(res) != 0:
                duration = step[s]
                num = int(res[0][1])

                return int(Now()) - duration * num 
    
    return None

def Strptime(timestring:str, format:str=None, utc:bool=False) -> int:
    """
    It takes a string of a date and time, and a format string, and returns the Unix timestamp of that
    date and time
    
    :param format: The format of the timestring
    :type format: str
    :param timestring: The string to be converted to a timestamp
    :type timestring: str
    :return: The timestamp of the datetime object.
    """

    from dateutil.parser import parse as dateparser
    from dateutil.parser import ParserError
    from ..String import String
    import datetime
    from datetime import datetime
    from dateutil import tz

    timestring = timestring.lower()

    if format:
        dtimestamp = datetime.strptime(timestring, format).timestamp()
    else:
        if len(String(timestring).RegexFind('([0-9]+)([smhdw])')) != 0:
            dtimestamp = parseTimeago(timestring)
            if not dtimestamp:
                raise Exception(f"不能解析时间字符串: {timestring}")
        else:
            try:
                dtimestamp = dateparser(timestring).timestamp()
            except ParserError as e:
                dtimestamp = parseTimeago(timestring)
                if not dtimestamp:
                    raise Exception(f"不能解析时间字符串: {timestring}")
    
    timestamp = int(round(dtimestamp))
    if utc == True:
        now_local = datetime.now(tz.tzlocal())
        offset = now_local.utcoffset().total_seconds()

        # 在 Strptime 函数中，当 utc 参数为 True 时，你在将时间戳转换为 UTC 时间时，增加了本地时间与 UTC 时间的偏移量。这是因为当你从本地时间转换为 UTC 时间时，你需要考虑到本地时间与 UTC 时间之间的时差，即偏移量。
        # 在这段代码中，通过获取当前本地时间 now_local，然后使用 utcoffset().total_seconds() 获取本地时间与 UTC 时间的偏移量，最后将这个偏移量加到时间戳上，以便转换为 UTC 时间。
        # 这是必要的，因为时间戳本身是与时区无关的，它代表的是从某个特定时间点（通常是 Unix 时间戳的起始时间）开始经过的秒数。因此，在将时间戳转换为特定时区的日期和时间时，必须考虑该时区的偏移量。
        timestamp = timestamp + offset

    return int(timestamp)

def DailyTimeBetween(start:str="00:00:00", end:str="07:00:00", now:float|int|str=None) -> bool:
    """
    This function checks if a given time falls between a start and end time.
    
    :param start: A string representing the starting time of a daily time interval in the format
    "HH:MM:SS", defaults to 00:00:00
    :type start: str (optional)
    :param end: The "end" parameter is a string representing the end time of a daily time interval in
    the format "HH:MM:SS". It defaults to "07:00:00", defaults to 07:00:00
    :type end: str (optional)
    :param now: The current time in either a string format (e.g. "12:30:00") or a float/int format
    representing the number of seconds since the epoch (e.g. 1612345678.0)
    :type now: float|int|str
    :return: a boolean value indicating whether the current time (represented by the `now` parameter) is
    between the start and end times (represented by the `start` and `end` parameters).
    """
    starttimestamp = Strptime(start)
    endtimestamp = Strptime(end)
    if type(now) == str:
        now = Strptime(now)
    elif now == None:
        now = Now()

    if endtimestamp < starttimestamp:
        endtimestamp += 86400

    return starttimestamp < now and now < endtimestamp

if __name__ == "__main__":
    # print(Strptime("2022-05-02 23:34:10", "%Y-%m-%d %H:%M:%S"))
    # print(Strftime(1651520050, "%Y-%m-%d %H:%M:%S"))
    # print(Strftime(Now()))
    # print(Strptime("2017-05-16T04:28:13.000000Z"))

    # print(Strptime("6 months ago"))
    # print(Strftime(Strptime("6 months ago")))
    # print(Strptime("just now"))
    # print(Strftime(Strptime("just now")))
    # print(Strptime("1 second ago"))
    # print(Strftime(Strptime("1 second ago")))
    # print(Strptime("in 24 days"))
    # print(Strftime(Strptime("in 24 days")))

    # print(FormatDuration(1750))
    # print(Strftime(Strptime("4m"))) # 4分钟前
    # print(Strftime(Strptime("2h"))) # 2小时前

    print(Strftime(Strptime("3 mo. ago"))) # 3个月前
    print(Strftime(Strptime("3 yr. ago"))) # 3年前