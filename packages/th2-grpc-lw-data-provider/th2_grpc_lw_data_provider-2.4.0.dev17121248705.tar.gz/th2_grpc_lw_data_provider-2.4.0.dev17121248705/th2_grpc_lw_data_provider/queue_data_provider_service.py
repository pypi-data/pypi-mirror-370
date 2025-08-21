from . import queue_data_provider_pb2_grpc as importStub

class QueueDataProviderService(object):

    def __init__(self, router):
        self.connector = router.get_connection(QueueDataProviderService, importStub.QueueDataProviderStub)

    def SearchMessageGroups(self, request, timeout=None, properties=None):
        return self.connector.create_request('SearchMessageGroups', request, timeout, properties)

    def SearchEvents(self, request, timeout=None, properties=None):
        return self.connector.create_request('SearchEvents', request, timeout, properties)