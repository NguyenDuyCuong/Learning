import datetime

x = datetime.datetime.now()
print(x)
print(x.year)
print(x.strftime("%A"))

x = datetime.datetime(2018, 6, 1)
print(x.strftime("%B"))