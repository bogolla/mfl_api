from django.test import TestCase
from model_mommy import mommy

from chul import models
from common.tests import ModelReprMixin


class TestModelRepr(ModelReprMixin, TestCase):

    def test_status(self):
        x = "hey ya"
        self.check_repr(models.Status.objects.create(name=x), x)

    def test_approver(self):
        x = "yo"
        self.check_repr(
            models.Approver.objects.create(name=x, abbreviation=x), x
        )

    def test_approval_status(self):
        x = "hihi"
        self.check_repr(models.ApprovalStatus.objects.create(name=x), x)

    def test_chu(self):
        x = "si-hech-yu"
        instance = mommy.make(models.CommunityHealthUnit, name=x, )
        self.check_repr(instance, x)

    def test_chu_contact(self):
        ct = models.Contact._meta.get_field(
            "contact_type").related_model.objects.create(name="twirra")
        contact = models.Contact.objects.create(contact="@m", contact_type=ct)
        chu = mommy.make(models.CommunityHealthUnit, name="c-h-u")
        chu_contact = models.CommunityHealthUnitContact.objects.create(
            health_unit=chu, contact=contact
        )
        self.check_repr(chu_contact, "c-h-u: (twirra: @m)")

    def test_chu_approval(self):
        ap_s = models.ApprovalStatus.objects.create(name="hehe")
        chu = mommy.make(models.CommunityHealthUnit, name="name")
        instance = mommy.make(
            models.CommunityHealthUnitApproval, approval_status=ap_s,
            health_unit=chu
        )
        self.check_repr(instance, "name: hehe")

    def test_chw(self):
        instance = mommy.make(
            models.CommunityHealthWorker, first_name="fname", id_number="123",
        )
        self.check_repr(instance, "fname (123)")

    def test_chw_contact(self):
        ct = models.Contact._meta.get_field(
            "contact_type").related_model.objects.create(name="twirra")
        contact = models.Contact.objects.create(contact="@m", contact_type=ct)
        chw = mommy.make(
            models.CommunityHealthWorker, first_name="fname", id_number="123",
        )
        chw_contact = models.CommunityHealthWorkerContact.objects.create(
            health_worker=chw, contact=contact
        )
        self.check_repr(chw_contact, "fname (123): (twirra: @m)")

    def test_chw_approval(self):
        ap_s = models.ApprovalStatus.objects.create(name="hehe")
        chw = mommy.make(
            models.CommunityHealthWorker, first_name="fname", id_number="123",
        )
        instance = mommy.make(
            models.CommunityHealthWorkerApproval, approval_status=ap_s,
            health_worker=chw
        )
        self.check_repr(instance, "fname (123): hehe")
