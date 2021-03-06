import reversion

from django.db import models
from django.utils import timezone, encoding

from common.models import AbstractBase, Contact, SequenceMixin
from common.fields import SequenceField
from facilities.models import Facility


@reversion.register
@encoding.python_2_unicode_compatible
class Status(AbstractBase):

    """
    Indicates the of operation of a community health unit.
    e.g  fully-functional, semi-functional, functional
    """
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta(AbstractBase.Meta):
        verbose_name_plural = 'statuses'


@reversion.register
@encoding.python_2_unicode_compatible
class Approver(AbstractBase):

    """
    These are the bodies or the people that approve a community health unit.
    """
    name = models.CharField(
        max_length=150, help_text='name of the approver', unique=True)
    description = models.TextField(null=True, blank=True)
    abbreviation = models.CharField(
        max_length=50, help_text='A short name for the approver.')

    def __str__(self):
        return self.name


@reversion.register
@encoding.python_2_unicode_compatible
class ApprovalStatus(AbstractBase):

    """
    Status of a community health unit indicating whether it has been
    approved or not.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta(AbstractBase.Meta):
        verbose_name_plural = 'approval_statuses'


@reversion.register(follow=['health_unit', 'contact'])
@encoding.python_2_unicode_compatible
class CommunityHealthUnitContact(AbstractBase):

    """
    The contacts of the health unit may be email, fax mobile etc.
    """
    health_unit = models.ForeignKey('CommunityHealthUnit')
    contact = models.ForeignKey(Contact)

    def __str__(self):
        return "{}: ({})".format(self.health_unit, self.contact)


@reversion.register(follow=['facility', 'status', 'contacts'])
@encoding.python_2_unicode_compatible
class CommunityHealthUnit(SequenceMixin, AbstractBase):

    """
    This is a health service delivery structure within a defined geographical
    area covering a population of approximately 5,000 people.

    Each unit is assigned 2 Community Health Extension Workers (CHEWs) and
    community health volunteers who offer promotive, preventative and basic
    curative health services
    """
    name = models.CharField(max_length=100)
    code = SequenceField(unique=True)
    facility = models.ForeignKey(
        Facility,
        help_text='The facility on which the health unit is tied to.')
    status = models.ForeignKey(Status)
    households_monitored = models.PositiveIntegerField(default=0)
    date_established = models.CharField(max_length=100, null=True, blank=True)
    contacts = models.ManyToManyField(
        Contact, through=CommunityHealthUnitContact)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_next_code_sequence()
        super(CommunityHealthUnit, self).save(*args, **kwargs)


class EntityApprovalAbstractBase(AbstractBase):

    """
    Links an entity to its approver.
    """
    approver = models.ForeignKey(Approver)
    approval_status = models.ForeignKey(ApprovalStatus)
    comment = models.TextField()
    approval_date = models.DateField(default=timezone.now)

    class Meta(AbstractBase.Meta):
        abstract = True


@reversion.register(follow=['approver', 'approval_status', 'health_unit', ])
@encoding.python_2_unicode_compatible
class CommunityHealthUnitApproval(EntityApprovalAbstractBase):

    """
    Links a community health unit to its approver.
    """
    health_unit = models.ForeignKey(
        CommunityHealthUnit,
        related_name='health_unit_approvals')

    def __str__(self):
        return "{}: {}".format(self.health_unit, self.approval_status)


@reversion.register(follow=['health_worker', 'contact'])
@encoding.python_2_unicode_compatible
class CommunityHealthWorkerContact(AbstractBase):

    """
    The contacts of the healh worker.

    They may be as many as the health worker has.
    """
    health_worker = models.ForeignKey('CommunityHealthWorker')
    contact = models.ForeignKey(Contact)

    def __str__(self):
        return "{}: ({})".format(self.health_worker, self.contact)


@reversion.register(follow=['health_unit', 'contacts'])
@encoding.python_2_unicode_compatible
class CommunityHealthWorker(AbstractBase):

    """
    A person who is incharge of a certain community health area.

    The status of the worker that is whether still active or not will be
    shown by the active field inherited from abstract base.
    """
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    id_number = models.PositiveIntegerField(unique=True, null=True, blank=True)
    health_unit = models.ForeignKey(
        CommunityHealthUnit,
        help_text='The health unit the worker is incharge of',
        related_name='health_unit_workers')
    contacts = models.ManyToManyField(
        Contact, through=CommunityHealthWorkerContact)

    def __str__(self):
        return "{} ({})".format(self.first_name, self.id_number)

    class Meta(AbstractBase.Meta):
        unique_together = ('id_number', 'health_unit')

    @property
    def name(self):
        return "{} {}".format(self.first_name, self.last_name).strip()


@reversion.register(follow=['approver', 'approval_status', 'health_worker', ])
@encoding.python_2_unicode_compatible
class CommunityHealthWorkerApproval(EntityApprovalAbstractBase):

    """
    Shows when a health worker was approved and by who.
    """
    health_worker = models.ForeignKey(
        CommunityHealthWorker, related_name='health_worker_approvals')

    def __str__(self):
        return "{}: {}".format(self.health_worker, self.approval_status)
