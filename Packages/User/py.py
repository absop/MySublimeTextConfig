import os

dir = 'D:/SublimeText3/Data/Packages/User'
for file in os.listdir():
    path = os.path.join(dir, file)
    if path.endswith('(Flake8Lint).tmTheme'):
        os.remove(path)
