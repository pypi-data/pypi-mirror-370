import reltest
import os

file_name = "reltesttest genextreme 1.txt"
file_path = os.getcwd() + '\\reltest output\\' + file_name
#with open(file_path, 'w') as f:
#    reltest.reltest_genextreme(f)

# ...


with open(file_path, 'r') as f:
    reltest.plot(f)