from kiota_abstractions.serialization.additional_data_holder import AdditionalDataHolder
from kiota_abstractions.serialization.parsable import Parsable
from kiota_abstractions.serialization.serialization_writer import SerializationWriter
from kiota_abstractions.store.backed_model import BackedModel
from kiota_abstractions.store.backing_store import BackingStore
from kiota_abstractions.store.backing_store_factory_singleton import BackingStoreFactorySingleton


class LargeFileUploadCreateSessionBody(Parsable, AdditionalDataHolder, BackedModel):

    def __init__(self):
        singleton = BackingStoreFactorySingleton.get_instance()
        factory = singleton.backing_store_factory
        self.backing_store = factory.create_backing_store(
        )  # throws error -AttributeError: type object
        #'BackingStoreFactorySingleton' has no attribute
        #  '_BackingStoreFactorySingleton__instance'
        self.set_additional_data([])

    def get_additional_data(self):
        return self.backing_store.get('additional_data')

    def set_additional_data(self, value):
        self.backing_store.set('additional_data', value)

    def get_field_deserializers(self):
        return {}

    def serialize(self, writer: SerializationWriter):
        writer.write_additional_data_value(self.get_additional_data())

    def get_backing_store(self):
        return self.backing_store
