class DeviceConnector(object):
    def open(self):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()

    def run(self):
        raise NotImplementedError()
