from . import lw_data_provider_pb2_grpc as importStub

class DataProviderService(object):

    def __init__(self, router):
        self.connector = router.get_connection(DataProviderService, importStub.DataProviderStub)

    def GetEvent(self, request, timeout=None, properties=None):
        return self.connector.create_request('GetEvent', request, timeout, properties)

    def GetMessage(self, request, timeout=None, properties=None):
        return self.connector.create_request('GetMessage', request, timeout, properties)

    def GetMessageStreams(self, request, timeout=None, properties=None):
        return self.connector.create_request('GetMessageStreams', request, timeout, properties)

    def SearchMessages(self, request, timeout=None, properties=None):
        return self.connector.create_request('SearchMessages', request, timeout, properties)

    def SearchEvents(self, request, timeout=None, properties=None):
        return self.connector.create_request('SearchEvents', request, timeout, properties)

    def SearchMessageGroups(self, request, timeout=None, properties=None):
        return self.connector.create_request('SearchMessageGroups', request, timeout, properties)

    def GetBooks(self, request, timeout=None, properties=None):
        return self.connector.create_request('GetBooks', request, timeout, properties)

    def GetPageInfo(self, request, timeout=None, properties=None):
        return self.connector.create_request('GetPageInfo', request, timeout, properties)