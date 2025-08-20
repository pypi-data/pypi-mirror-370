import os

import pytest

from tests.enums.tools import Toolkit, CloudTool
from codemie_sdk.models.integration import CredentialTypes
from tests.utils.aws_parameters_store import CredentialsUtil

cloud_test_data = [
    (
        Toolkit.CLOUD,
        CloudTool.AWS,
        CredentialTypes.AWS,
        CredentialsUtil.aws_credentials(),
        {
            "query": {
                "service": "s3",
                "method_name": "list_buckets",
                "method_arguments": {},
            }
        },
        """
            {
               "ResponseMetadata":{
                  "RequestId":"7F5A7MRRFPY9RPTC",
                  "HostId":"YDtbO8lMQau9e0tDDDDC0GGnZnqQb1RxW9bRHQcV3P6v/FhWgLyVS63l79oBVOchAzQ9AXZeY1kCmeUWsoUTYg==",
                  "HTTPStatusCode":200,
                  "HTTPHeaders":{
                     "x-amz-id-2":"YDtbO8lMQau9e0tDDDDC0GGnZnqQb1RxW9bRHQcV3P6v/FhWgLyVS63l79oBVOchAzQ9AXZeY1kCmeUWsoUTYg==",
                     "x-amz-request-id":"7F5A7MRRFPY9RPTC",
                     "date":"Wed, 25 Jun 2025 15:39:54 GMT",
                     "content-type":"application/xml",
                     "transfer-encoding":"chunked",
                     "server":"AmazonS3"
                  },
                  "RetryAttempts":0
               },
               "Buckets":[
                  {
                     "Name":"az-v3-codemie-terraform-states-025066278959",
                     "CreationDate": datetime.datetime(2025, 6, 20, 13, 31, 10, tzinfo=tzlocal())
                  },
                  {
                     "Name":"codemie-bucket",
                     "CreationDate": datetime.datetime(2025, 1, 29, 17, 30, 57, tzinfo=tzlocal())
                  },
                  {
                     "Name":"codemie-it-terraform-states-025066278959",
                     "CreationDate": datetime.datetime(2025, 6, 16, 21, 30, 46, tzinfo=tzlocal())
                  },
                  {
                     "Name":"codemie-it-user-data-025066278959",
                     "CreationDate": datetime.datetime(2025, 6, 16, 21, 30, 48, tzinfo=tzlocal())
                  },
                  {
                     "Name":"codemie-terraform-states-025066278959",
                     "CreationDate": datetime.datetime(2025, 6, 13, 13, 30, 50, tzinfo=tzlocal())
                  },
                  {
                     "Name":"codemie-terraform-states-yevhen-l-025066278959",
                     "CreationDate": datetime.datetime(2025, 6, 17, 9, 30, 58, tzinfo=tzlocal())
                  },
                  {
                     "Name":"codemie-user-data-025066278959",
                     "CreationDate": datetime.datetime(2025, 6, 16, 13, 31, 5, tzinfo=tzlocal())
                  },
                  {
                     "Name":"codemie-yl-user-data-025066278959",
                     "CreationDate": datetime.datetime(2025, 6, 17, 11, 31, 1, tzinfo=tzlocal())
                  },
                  {
                     "Name":"epam-cloud-s3-access-logs-025066278959-eu-central-1",
                     "CreationDate": datetime.datetime(2024, 11, 9, 19, 51, 46, tzinfo=tzlocal())
                  },
                  {
                     "Name":"epam-cloud-s3-access-logs-025066278959-eu-north-1",
                     "CreationDate": datetime.datetime(2025, 5, 17, 15, 31, 2, tzinfo=tzlocal())
                  },
                  {
                     "Name":"epam-cloud-s3-access-logs-025066278959-eu-west-2",
                     "CreationDate": datetime.datetime(2025, 5, 21, 15, 30, 57, tzinfo=tzlocal())

                  },
                  {
                     "Name":"epam-cloud-s3-access-logs-025066278959-us-east-1",
                     "CreationDate": datetime.datetime(2024, 11, 27, 15, 31, tzinfo=tzlocal())
                  },
                  {
                     "Name":"sk-codemie-terraform-states-025066278959",
                     "CreationDate": datetime.datetime(2025, 6, 4, 15, 30, 48, tzinfo=tzlocal())
                  },
                  {
                     "Name":"terraform-states-025066278959",
                     "CreationDate": datetime.datetime(2024, 11, 13, 22, 30, 57, tzinfo=tzlocal())
                  }
               ],
               "Owner":{
                  "ID":"978dcce1304506a42ed130c2cfdd87fe9c0652869232df15b4b5589a6481d4e5"
               }
            }
        """,
    ),
    (
        Toolkit.CLOUD,
        CloudTool.AZURE,
        CredentialTypes.AZURE,
        CredentialsUtil.azure_credentials(),
        {
            "method": "GET",
            "url": "https://management.azure.com/subscriptions/08679d2f-8945-4e08-8df8-b8e58626b13a/resourceGroups/krci-codemie-azure-env-rg?api-version=2021-04-01",
        },
        """
            {
              "id" : "/subscriptions/08679d2f-8945-4e08-8df8-b8e58626b13a/resourceGroups/krci-codemie-azure-env-rg",
              "name" : "krci-codemie-azure-env-rg",
              "type" : "Microsoft.Resources/resourceGroups",
              "location" : "westeurope",
              "tags" : {
                "environment" : "codemie-azure"
              },
              "properties" : {
                "provisioningState" : "Succeeded"
              }
            }
        """,
    ),
    pytest.param(
        Toolkit.CLOUD,
        CloudTool.GCP,
        CredentialTypes.GCP,
        CredentialsUtil.gcp_credentials(),
        {
            "method": "GET",
            "scopes": ["https://www.googleapis.com/auth/cloud-platform"],
            "url": "https://www.googleapis.com/storage/v1/b/009fb622-4e29-42aa-bafd-584c61f5e1e1",
        },
        """
            {
               "kind":"storage#bucket",
               "selfLink":"https://www.googleapis.com/storage/v1/b/009fb622-4e29-42aa-bafd-584c61f5e1e1",
               "id":"009fb622-4e29-42aa-bafd-584c61f5e1e1",
               "name":"009fb622-4e29-42aa-bafd-584c61f5e1e1",
               "projectNumber":"415940185513",
               "generation":"1731334834610581052",
               "metageneration":"1",
               "location":"US",
               "storageClass":"STANDARD",
               "etag":"CAE=",
               "timeCreated":"2024-11-11T14:20:34.897Z",
               "updated":"2024-11-11T14:20:34.897Z",
               "softDeletePolicy":{
                  "retentionDurationSeconds":"604800",
                  "effectiveTime":"2024-11-11T14:20:34.897Z"
               },
               "iamConfiguration":{
                  "bucketPolicyOnly":{
                     "enabled":false
                  },
                  "uniformBucketLevelAccess":{
                     "enabled":false
                  },
                  "publicAccessPrevention":"inherited"
               },
               "locationType":"multi-region",
               "rpo":"DEFAULT"
            }
        """,
        marks=pytest.mark.skipif(
            os.getenv("ENV") == "azure",
            reason="Still have an issue with encoding long strings",
        ),
    ),
]
