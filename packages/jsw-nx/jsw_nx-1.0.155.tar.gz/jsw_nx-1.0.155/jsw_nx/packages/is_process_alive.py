import psutil


# https://thispointer.com/python-check-if-a-process-is-running-by-name-and-find-its-process-id-pid/

def is_process_alive(in_process_name):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    # Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            std_name = in_process_name.lower()
            if std_name.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False
