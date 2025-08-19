import datetime as dt
class TimeTracker:
	def __init__(A):A.start_time=dt.datetime.now(dt.timezone.utc);A.end_time=None
	def stop(A):A.end_time=dt.datetime.now(dt.timezone.utc)
	def get_datetime_data(B,datetime):A=datetime;return{'datetime':A.strftime('%Y-%m-%d %H:%M:%S'),'date':A.strftime('%Y-%m-%d'),'time':A.strftime('%H:%M:%S')}
	def get_data(A):return{'start':A.get_datetime_data(A.start_time),'end':A.get_datetime_data(A.end_time)if A.end_time else None,'duration_seconds':(A.end_time-A.start_time).total_seconds()if A.end_time else None}