# from datetime import datetime

# cdt = datetime.now()
# fdt = cdt.strftime('%Y-%m-%d_%H%M%S')
# print (fdt)

s = '355 ₽302'
s_lst = s.split(' ₽')
ss = int(s_lst[-1])
print(ss)