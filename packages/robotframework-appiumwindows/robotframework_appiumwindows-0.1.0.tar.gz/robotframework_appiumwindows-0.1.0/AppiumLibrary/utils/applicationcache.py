from robot.utils import ConnectionCache


class ApplicationCache(ConnectionCache):

    def __init__(self):
        ConnectionCache.__init__(self, no_current_msg='No current application')
        self._closed = set()

    @property
    def applications(self):
        return self._connections

    def get_open_browsers(self):
        open_applications = []
        for application in self._connections:
            if application not in self._closed:
                open_applications.append(application)
        return open_applications

    def close(self, ignore_fail=False, quit_app=True):
        if self.current:
            application = self.current
            try:
                if quit_app:
                    application.quit()
                else:
                    application.close()
            except Exception as err:
                if not ignore_fail:
                    raise err
            self.current = self._no_current
            self.current_index = None
            self._closed.add(application)

    def close_all(self, ignore_fail=True, quit_app=True):
        for application in self._connections:
            if application not in self._closed:
                try:
                    if quit_app:
                        application.quit()
                    else:
                        application.close()
                except Exception as err:
                    if not ignore_fail:
                        raise err
        self.empty_cache()
        return self.current
