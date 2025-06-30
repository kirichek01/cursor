import os
os.environ['QT_API'] = 'pyside6'
import qtpy
print("Используемый биндинг:", qtpy.API)