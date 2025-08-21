import os


class Pm2Manager:
    def __init__(self):
        pass

    @staticmethod
    def start(app_name='all'):
        os.system(f'pm2 start {app_name}')

    @staticmethod
    def stop(app_name='all'):
        os.system(f'pm2 stop {app_name}')

    @staticmethod
    def restart(app_name='all'):
        os.system(f'pm2 restart {app_name}')

    @staticmethod
    def delete(app_name='all'):
        os.system(f'pm2 delete {app_name}')

    @staticmethod
    def stop_and_del(app_name='all'):
        os.system(f'pm2 stop {app_name}')
        os.system(f'pm2 delete {app_name}')
