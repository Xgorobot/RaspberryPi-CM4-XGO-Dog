from demos.uiutils import *
import time
lang=language()
print(lang)
if lang=='cn':
	 print('lang = cn')
	 os.system('sudo python3 main.py')
	 
else:
     print('lang = en')
     os.system('sudo -E python3 main.py')


