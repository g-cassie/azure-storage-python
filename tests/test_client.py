﻿#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------
import unittest
from azure.storage.blob import (
    BlockBlobService,
    PageBlobService,
    AppendBlobService,
)
from azure.storage.queue import QueueService
from azure.storage.table import TableService
from azure.storage.file import FileService
from tests.testcase import (
    StorageTestCase,
    record,
)

#------------------------------------------------------------------------------
SERVICES = {
    BlockBlobService: 'blob',
    PageBlobService: 'blob',
    AppendBlobService: 'blob',
    QueueService: 'queue',
    TableService: 'table',
    FileService: 'file'
}

class StorageClientTest(StorageTestCase):

    def setUp(self):
        super(StorageClientTest, self).setUp()
        self.account_name = self.settings.STORAGE_ACCOUNT_NAME
        self.account_key = self.settings.STORAGE_ACCOUNT_KEY
        self.sas_token = '?sv=2015-04-05&st=2015-04-29T22%3A18%3A26Z&se=2015-04-30T02%3A23%3A26Z&sr=b&sp=rw&sip=168.1.5.60-168.1.5.70&spr=https&sig=Z%2FRHIX5Xcg0Mq2rqI3OlWTjEg2tYkboXr1P9ZUXDtkk%3D'

    #--Helpers-----------------------------------------------------------------
    def validate_standard_account_endpoints(self, service, type):
        self.assertIsNotNone(service)
        self.assertEqual(service.account_name, self.account_name)
        self.assertEqual(service.account_key, self.account_key)
        self.assertEqual(service.primary_endpoint, '{}.{}.core.windows.net'.format(self.account_name, type))
        self.assertEqual(service.secondary_endpoint, '{}-secondary.{}.core.windows.net'.format(self.account_name, type))

    #--Direct Parameters Test Cases --------------------------------------------
    def test_create_service_with_key(self):
        # Arrange
   
        for type in SERVICES.items():
            # Act
            service = type[0](self.account_name, self.account_key)

            # Assert
            self.validate_standard_account_endpoints(service, type[1])
            self.assertEqual(service.protocol, 'https')

    def test_create_service_with_sas(self):
        # Arrange
   
        for type in SERVICES:
            # Act
            service = type(self.account_name, sas_token=self.sas_token)

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, self.account_name)
            self.assertEqual(service.sas_token, self.sas_token)
            self.assertIsNone(service.account_key)

    def test_create_service_china(self):
        # Arrange

        for type in SERVICES.items():
            # Act
            service = type[0](self.account_name, self.account_key, endpoint_suffix='core.chinacloudapi.cn')

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, self.account_name)
            self.assertEqual(service.account_key, self.account_key)
            self.assertEqual(service.primary_endpoint, '{}.{}.core.chinacloudapi.cn'.format(self.account_name, type[1]))
            self.assertEqual(service.secondary_endpoint, '{}-secondary.{}.core.chinacloudapi.cn'.format(self.account_name, type[1]))

    def test_create_service_protocol(self):
        # Arrange
   
        for type in SERVICES.items():
            # Act
            service = type[0](self.account_name, self.account_key, protocol='http')

            # Assert
            self.validate_standard_account_endpoints(service, type[1])
            self.assertEqual(service.protocol, 'http')

    def test_create_service_with_emulator(self):
        # Arrange

        # Act
        service = BlockBlobService(is_emulated=True)

        # Assert
        self.assertIsNotNone(service)
        self.assertEqual(service.account_name, 'devstoreaccount1')
        self.assertIsNotNone(service.account_key)
        self.assertEqual(service.protocol, 'http')
        self.assertEqual(service.primary_endpoint, '127.0.0.1:10000/devstoreaccount1')
        self.assertEqual(service.secondary_endpoint, '127.0.0.1:10000/devstoreaccount1-secondary')

    def test_create_blob_service_anonymous(self):
        # Arrange
        BLOB_SERVICES = [BlockBlobService, PageBlobService, AppendBlobService]

        for type in BLOB_SERVICES:
            # Act
            service = type(self.account_name)

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, self.account_name)
            self.assertIsNone(service.account_key)
            self.assertIsNone(service.sas_token)

    def test_create_blob_service_custom_domain(self):
        # Arrange
        BLOB_SERVICES = [BlockBlobService, PageBlobService, AppendBlobService]

        for type in BLOB_SERVICES:
            # Act
            service = type(self.account_name, self.account_key, custom_domain='www.mydomain.com')

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, self.account_name)
            self.assertEqual(service.account_key, self.account_key)
            self.assertEqual(service.primary_endpoint, 'www.mydomain.com')
            self.assertEqual(service.secondary_endpoint, self.account_name + '-secondary.blob.core.windows.net')

    def test_create_service_empty_key(self):
        # Arrange
        NON_BLOB_SERVICES = [QueueService, TableService, FileService]
   
        for type in NON_BLOB_SERVICES:
            # Act
            try:
                table_service = type('testaccount', '')
                self.fail('Passing an empty key to create account should fail.')
            except ValueError as e:
                self.assertTrue(str(e) == 'You need to provide an account name and either an account_key or sas_token when creating a storage service.')

    def test_create_service_missing_arguments(self):
        # Arrange
   
        for type in SERVICES:
            # Act
            with self.assertRaises(ValueError):
                service = type()

        # Assert

    #--Connection String Test Cases --------------------------------------------

    def test_create_service_with_connection_string_key(self):
        # Arrange
        conn_string = 'AccountName={};AccountKey={};'.format(self.account_name, self.account_key)

        for type in SERVICES.items():
            # Act
            service = type[0](connection_string=conn_string)

            # Assert
            self.validate_standard_account_endpoints(service, type[1])
            self.assertEqual(service.protocol, 'https')

    def test_create_service_with_connection_string_sas(self):
        # Arrange
        conn_string = 'AccountName={};SharedAccessSignature={};'.format(self.account_name, self.sas_token)
   
        for type in SERVICES:
            # Act
            service = type(connection_string=conn_string)

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, self.account_name)
            self.assertEqual(service.sas_token, self.sas_token)
            self.assertIsNone(service.account_key)

    def test_create_service_with_connection_string_endpoint_protocol(self):
        # Arrange
        conn_string = 'AccountName={};AccountKey={};DefaultEndpointsProtocol=http;EndpointSuffix=core.chinacloudapi.cn;'.format(self.account_name, self.account_key)

        for type in SERVICES.items():
            # Act
            service = type[0](connection_string=conn_string)

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, self.account_name)
            self.assertEqual(service.account_key, self.account_key)
            self.assertEqual(service.primary_endpoint, '{}.{}.core.chinacloudapi.cn'.format(self.account_name, type[1]))
            self.assertEqual(service.secondary_endpoint, '{}-secondary.{}.core.chinacloudapi.cn'.format(self.account_name, type[1]))
            self.assertEqual(service.protocol, 'http')

    def test_create_service_with_connection_string_emulated(self):
        # Arrange
        conn_string = 'UseDevelopmentStorage=true;'.format(self.account_name, self.account_key)

        # Act
        service = BlockBlobService(connection_string=conn_string)

        # Assert
        self.assertIsNotNone(service)
        self.assertEqual(service.account_name, 'devstoreaccount1')
        self.assertIsNotNone(service.account_key)
        self.assertEqual(service.protocol, 'http')
        self.assertEqual(service.primary_endpoint, '127.0.0.1:10000/devstoreaccount1')
        self.assertEqual(service.secondary_endpoint, '127.0.0.1:10000/devstoreaccount1-secondary')

    def test_create_service_with_connection_string_emulated_explicit(self):
        # Arrange
        conn_string = 'DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;TableEndpoint=http://127.0.0.1:10002/devstoreaccount1;QueueEndpoint=http://127.0.0.1:10001/devstoreaccount1;' \
            .format(self.account_name, self.account_key)

        # Act
        service = BlockBlobService(connection_string=conn_string)

        # Assert
        self.assertIsNotNone(service)
        self.assertEqual(service.account_name, 'devstoreaccount1')
        self.assertIsNotNone(service.account_key)
        self.assertEqual(service.protocol, 'http')
        self.assertEqual(service.primary_endpoint, '127.0.0.1:10000/devstoreaccount1')

    def test_create_service_with_connection_string_anonymous(self):
        # Arrange
        conn_string = 'BlobEndpoint=www.mydomain.com;'

        # Act
        service = BlockBlobService(connection_string=conn_string)

        # Assert
        self.assertIsNotNone(service)
        self.assertIsNone(service.account_name)
        self.assertIsNone(service.account_key)
        self.assertIsNone(service.sas_token)
        self.assertEqual(service.primary_endpoint, 'www.mydomain.com')

    def test_create_service_with_connection_string_custom_domain(self):
        # Arrange
        conn_string = 'AccountName={};AccountKey={};BlobEndpoint=www.mydomain.com;'.format(self.account_name, self.account_key)

        # Act
        service = BlockBlobService(connection_string=conn_string)

        # Assert
        self.assertIsNotNone(service)
        self.assertEqual(service.account_name, self.account_name)
        self.assertEqual(service.account_key, self.account_key)
        self.assertEqual(service.primary_endpoint, 'www.mydomain.com')
        self.assertEqual(service.secondary_endpoint, self.account_name + '-secondary.blob.core.windows.net')

    def test_create_service_with_connection_string_custom_domain_trailing_slash(self):
        # Arrange
        conn_string = 'AccountName={};AccountKey={};BlobEndpoint=www.mydomain.com/;'.format(self.account_name, self.account_key)

        # Act
        service = BlockBlobService(connection_string=conn_string)

        # Assert
        self.assertIsNotNone(service)
        self.assertEqual(service.account_name, self.account_name)
        self.assertEqual(service.account_key, self.account_key)
        self.assertEqual(service.primary_endpoint, 'www.mydomain.com')
        self.assertEqual(service.secondary_endpoint, self.account_name + '-secondary.blob.core.windows.net')

    @record
    def test_request_callback_signed_header(self):
        # Arrange
        service = BlockBlobService(self.account_name, self.account_key)
        name = self.get_resource_name('cont')

        # Act
        def callback(request):
            if request.method == 'PUT':
                request.headers['x-ms-meta-hello'] = 'world'

        service.request_callback = callback

        # Assert
        try:
            service.create_container(name)
            metadata = service.get_container_metadata(name)
            self.assertEqual(metadata, {'hello': 'world'})
        finally:
            service.delete_container(name)

    @record
    def test_response_callback(self):
        # Arrange
        service = BlockBlobService(self.account_name, self.account_key)
        name = self.get_resource_name('cont')

        # Act
        def callback(response):
            response.status = 200
            response.headers.clear()

        # Force an exists call to succeed by resetting the status
        service.response_callback = callback

        # Assert
        exists = service.exists(name)
        self.assertTrue(exists)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
