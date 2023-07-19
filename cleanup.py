import os
for (dirpath, dirnames, filenames) in os.walk("./app/infrastructure/files/output/"):
    for filename in filenames:
        if filename.endswith('_temp.csv'):
            print(os.sep.join([dirpath, filename]))
            os.remove(os.sep.join([dirpath, filename]))
for (dirpath, dirnames, filenames) in os.walk("./app/infrastructure/files/temp/"):
    for filename in filenames:
        if filename.endswith('_temp.csv'):
            print(os.sep.join([dirpath, filename]))
            os.remove(os.sep.join([dirpath, filename]))