import multiprocessing

import flask_excel as excel

from app.models import *


# pyinstaller fixes

def process_exists(processname):
    tlcall = 'TASKLIST', '/FI', 'imagename eq %s' % processname
    # shell=True hides the shell window, stdout to PIPE enables
    # communicate() to get the tasklist command result
    tlproc = subprocess.Popen(tlcall, shell=True, stdout=subprocess.PIPE)
    # trimming it to the actual lines with information
    #tlout_0 = tlproc.communicate()[0]
    tlout_0 = tlproc.communicate()
    tlout = str(tlout_0).strip('\\r\\n').split('\\r\\n')
    #tlout_1 = str(tlout_0).strip().split('\r\n')
    #tlout = tlout_1
    running = 0
    for run in tlout:
        if run.__contains__(processname):
            running = running + 1

    # if TASKLIST returns single line without processname: it's not running
    if running > 1:
        # print(tlout)
        return True
    else:
        return False





@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}

if process_exists('run.exe'):
    print("Application is already running")
    raise SystemExit
else:
    if __name__ == '__main__':
        multiprocessing.freeze_support()
        excel.init_excel(app)
        import threading, webbrowser
        #port = 5000 + random.randint(0, 999)
        port = 4992
        url = "http://127.0.0.1:{0}".format(port)
        ##threading.Timer(1.25, lambda: webbrowser.open(url)).start()
        app.run(port=port, debug=False)
  #  app.run(debug=True, port=4992)
