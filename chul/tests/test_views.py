from django.core.urlresolvers import reverse

from model_mommy import mommy

from common.tests import ViewTestBase


from ..models import (
    CommunityHealthUnit,
    CommunityHealthWorker,
    CommunityHealthWorkerContact
)
from ..serializers import (
    CommunityHealthUnitSerializer,
    CommunityHealthWorkerSerializer,
    CommunityHealthWorkerContactSerializer
)


class TestCommunityHealthUnitView(ViewTestBase):

    def setUp(self):
        self.url = reverse("api:chul:community_health_units_list")
        super(TestCommunityHealthUnitView, self).setUp()

    def test_list_community_health_units(self):
        health_unit = mommy.make(CommunityHealthUnit)
        health_unit_2 = mommy.make(CommunityHealthUnit)
        response = self.client.get(self.url)
        expected_data = {
            "results": [
                CommunityHealthUnitSerializer(
                    health_unit_2,
                    context={
                        'request': response.request
                    }
                ).data,
                CommunityHealthUnitSerializer(
                    health_unit,
                    context={
                        'request': response.request
                    }
                ).data
            ]
        }
        self.assertEquals(200, response.status_code)
        self._assert_response_data_equality(
            expected_data['results'], response.data['results']
        )

    def test_retrieve_single_health_unit(self):
        health_unit = mommy.make(CommunityHealthUnit)
        url = self.url + "{}/".format(health_unit.id)
        response = self.client.get(url)
        expected_data = CommunityHealthUnitSerializer(
            health_unit,
            context={
                'request': response.request
            }
        ).data

        self.assertEquals(200, response.status_code)
        self._assert_response_data_equality(expected_data, response.data)


class TestCommunityHealthWorkerView(ViewTestBase):

    def setUp(self):
        self.url = reverse("api:chul:community_health_workers_list")
        super(TestCommunityHealthWorkerView, self).setUp()

    def test_health_workers_listing(self):
        worker_1 = mommy.make(CommunityHealthWorker)
        worker_2 = mommy.make(CommunityHealthWorker)
        response = self.client.get(self.url)
        expected_data = {
            "results": [
                CommunityHealthWorkerSerializer(
                    worker_2,
                    context={
                        'request': response.request
                    }
                ).data,
                CommunityHealthWorkerSerializer(
                    worker_1,
                    context={
                        'request': response.request
                    }
                ).data
            ]
        }
        self.assertEquals(200, response.status_code)
        self.maxDiff = None
        self._assert_response_data_equality(
            expected_data['results'], response.data['results']
        )

    def test_retrieve_single_worker(self):
        worker = mommy.make(CommunityHealthWorker)
        expected_data = CommunityHealthWorkerSerializer(
            worker, context={
                'request': {
                    "REQUEST_METHOD": "None"
                }
            }
        ).data
        url = self.url + "{}/".format(worker.id)
        response = self.client.get(url)
        self.assertEquals(200, response.status_code)
        self._assert_response_data_equality(expected_data, response.data)


class TestCommunityHealthWokerContactView(ViewTestBase):

    def setUp(self):
        self.url = reverse("api:chul:community_health_worker_contacts_list")
        super(TestCommunityHealthWokerContactView, self).setUp()

    def test_health_workers_contact_list(self):
        contact_1 = mommy.make(CommunityHealthWorkerContact)
        contact_2 = mommy.make(CommunityHealthWorkerContact)
        response = self.client.get(self.url)
        expected_data = {
            "results": [
                CommunityHealthWorkerContactSerializer(
                    contact_2,
                    context={
                        'request': response.request
                    }
                ).data,
                CommunityHealthWorkerContactSerializer(
                    contact_1,
                    context={
                        'request': response.request
                    }
                ).data
            ]
        }
        self.assertEquals(200, response.status_code)
        self._assert_response_data_equality(
            expected_data['results'], response.data['results']
        )

    def test_retrieve_single_health_worker_contact(self):
        contact = mommy.make(CommunityHealthWorkerContact)
        url = self.url + "{}/".format(contact.id)
        response = self.client.get(url)
        expected_data = CommunityHealthWorkerContactSerializer(
            contact,
            context={
                'request': response.request
            }
        ).data
        self.assertEquals(200, response.status_code)
        self._assert_response_data_equality(expected_data, response.data)
