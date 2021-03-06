import functools

from datetime import timedelta

from django.apps import apps
from django.db.models import Sum
from django.utils import timezone

from rest_framework.views import APIView, Response
from rest_framework.exceptions import NotFound

from facilities.models import (
    Facility,
    FacilityType,
    KephLevel,
    FacilityUpgrade)
from common.constants import TRUTH_NESS, FALSE_NESS
from common.models import County, Constituency

from .report_config import REPORTS


class FilterReportMixin(object):
    queryset = Facility.objects.all()

    def _prepare_filters(self, filtering_data):
        filtering_data = filtering_data.split('=')
        return filtering_data[0], filtering_data[1]

    def _build_dict_filter(self, filter_field_name, value):
        return {
            filter_field_name: value
        }

    def _filter_queryset(self, filter_dict):
        return self.queryset.filter(**filter_dict)

    def _filter_relation_obj(self, model, field_name, value):
        filter_dict = {
            field_name: value
        }
        return model.objects.filter(**filter_dict)

    def _filter_by_extra_params(
            self, report_config, more_filters_params, model):
        more_filters = self._prepare_filters(more_filters_params)

        requested_filters = report_config.get(
            'extra_filters')[more_filters[0]]
        requested_filters_filter_field_name = requested_filters.get(
            "filter_field_name")
        filtering_dict = self._build_dict_filter(
            requested_filters_filter_field_name, more_filters[1])

        self.queryset = self._filter_queryset(filtering_dict)
        model_instances = self._filter_relation_obj(
            model, more_filters[0], more_filters[1])
        return model_instances

    def _get_return_data(
            self, filter_field_name, model_instances, return_instance_name,
            return_count_name):
        data = []

        for instance in model_instances:
            filiter_data = {
                filter_field_name: instance
            }
            count = self.queryset.filter(**filiter_data).count()
            instance_name = instance.name
            data.append(
                {
                    return_instance_name: instance_name,
                    return_count_name: count
                }
            )
        return data

    def get_report_data(self, *args, **kwargs):
        report_type = self.request.query_params.get(
            "report_type", "facility_count_by_county")
        if report_type == "facility_count_by_facility_type_detailed":
            return self._get_facility_type_data()
        if report_type == "facility_keph_level_report":
            return self._get_facility_keph_level_data()
        if report_type == "facility_constituency_report":
            return self._get_facility_constituency_data()

        if report_type == "beds_and_cots_by_county":
            return self._get_beds_and_cots({
                'ward__constituency__county__name': 'county_name',
                'ward__constituency__county': 'county'
            })

        if report_type == "beds_and_cots_by_constituency":
            county_id = self.request.query_params.get("county", None)
            filters = (
                {} if county_id is None
                else {"ward__constituency__county": county_id}
            )
            return self._get_beds_and_cots(vals={
                'ward__constituency__name': 'constituency_name',
                'ward__constituency': 'constituency'
            }, filters=filters)

        if report_type == "beds_and_cots_by_ward":
            constituency_id = self.request.query_params.get(
                "constituency", None
            )
            filters = (
                {} if constituency_id is None
                else {"ward__constituency": constituency_id}
            )
            return self._get_beds_and_cots(
                vals={'ward__name': 'ward_name', 'ward': "ward"},
                filters=filters
            )

        more_filters_params = self.request.query_params.get("filters", None)

        report_config = REPORTS.get(report_type, None)
        if report_config is None:
            raise NotFound(detail="Report not found.")

        group_by = report_config.get("group_by")
        app_label, model_name = report_config.get(
            "filter_fields").get("model").split('.')
        filter_field_name = report_config.get(
            "filter_fields").get("filter_field_name")
        model = apps.get_model(app_label, model_name)
        model_instances = model.objects.all()

        if more_filters_params:
            model_instances = self._filter_by_extra_params(
                report_config, more_filters_params, model)

        return_instance_name = report_config.get(
            "filter_fields").get("return_field")[0]
        return_count_name = report_config.get(
            "filter_fields").get("return_field")[1]
        if group_by:
            pass
        else:
            data = self._get_return_data(
                filter_field_name, model_instances, return_instance_name,
                return_count_name)
        return data, self.queryset.count()

    def _get_facility_type_data(self):
        owner_category = self.request.query_params.get("owner_category")
        facility_type = self.request.query_params.get("facility_type")

        data = []

        for county in County.objects.all():
            for facility_type in FacilityType.objects.all():
                if not owner_category:
                    count = Facility.objects.filter(
                        facility_type=facility_type,
                        ward__constituency__county=county).count()
                else:
                    count = Facility.objects.filter(
                        facility_type=facility_type,
                        ward__constituency__county=county,
                        owner__owner_type=owner_category).count()

                data.append(
                    {
                        "county": county.name,
                        "facility_type": facility_type.name,
                        "number_of_facilities": count
                    }
                )

        totals = []

        return data, totals

    def _get_facility_keph_level_data(self):
        owner_category = self.request.query_params.get("owner_category")

        data = []

        for county in County.objects.all():
            for level in KephLevel.objects.all():
                if not owner_category:
                    count = Facility.objects.filter(
                        keph_level=level,
                        ward__constituency__county=county).count()
                else:
                    count = Facility.objects.filter(
                        level=level,
                        ward__constituency__county=county,
                        owner__owner_type=owner_category).count()

                data.append({
                    "county": county.name,
                    "keph_level": level.name,
                    "number_of_facilities": count
                })

        totals = []
        return data, totals

    def _get_facility_constituency_data(self):
        owner_category = self.request.query_params.get("owner_category")

        data = []

        for county in County.objects.all():
            for const in Constituency.objects.filter(county=county):
                if not owner_category:
                    count = Facility.objects.filter(
                        ward__constituency=const).count()
                else:
                    count = Facility.objects.filter(
                        ward__constituency=const,
                        owner__owner_type=owner_category).count()

                data.append({
                    "county": county.name,
                    "constituency": const.name,
                    "number_of_facilities": count
                })

            totals = []
        return data, totals

    def _get_beds_and_cots(self, vals={}, filters={}):
        fields = vals.keys()
        assert len(fields) == 2
        items = Facility.objects.values(*fields).filter(**filters).annotate(
            cots=Sum('number_of_cots'), beds=Sum('number_of_beds')
        ).order_by()

        total_cots, total_beds = functools.reduce(
            lambda x, y: (x[0]+y['cots'], x[1]+y['beds']),
            items, (0, 0)
        )

        return [
            {
                'cots': p['cots'],
                'beds': p['beds'],
                vals[fields[0]]: p[fields[0]],
                vals[fields[1]]: p[fields[1]]
            } for p in items
        ], {"total_cots": total_cots, "total_beds": total_beds}


class ReportView(FilterReportMixin, APIView):

    def get(self, *args, **kwargs):
        data, totals = self.get_report_data()

        return Response(data={
            "results": data,
            "total": totals
        })


class FacilityUpgradeDowngrade(APIView):

    def get(self, *args, **kwargs):
        county = self.request.query_params.get('county', None)
        upgrade = self.request.query_params.get('upgrade', None)

        right_now = timezone.now()
        last_week = self.request.query_params.get('last_week', None)
        last_month = self.request.query_params.get('last_month', None)
        last_three_months = self.request.query_params.get(
            'last_three_months', None)
        three_months_ago = right_now - timedelta(days=90)
        last_one_week = right_now - timedelta(days=7)
        last_one_month = right_now - timedelta(days=30)

        if upgrade in TRUTH_NESS:
            all_changes = FacilityUpgrade.objects.filter(
                is_upgrade=True)
        elif upgrade in FALSE_NESS:
            all_changes = FacilityUpgrade.objects.filter(
                is_upgrade=False)
        else:
            all_changes = FacilityUpgrade.objects.all()

        if last_week:
            all_changes = all_changes.filter(created__gte=last_one_week)
        if last_month:
            all_changes = all_changes.filter(created__gte=last_one_month)
        if last_three_months:
            all_changes = all_changes.filter(created__gte=three_months_ago)

        facilities_ids = [change.facility.id for change in all_changes]
        changed_facilities = Facility.objects.filter(id__in=facilities_ids)
        if not county:
            results = []
            for county in County.objects.all():
                facility_count = changed_facilities.filter(
                    ward__constituency__county=county).count()
                data = {
                    "county": county.name,
                    "county_id": county.id,
                    "changes": facility_count
                }
                results.append(data)
            return Response(data={
                "total_number_of_changes": len(facilities_ids),
                "results": results
            })
        else:

            facilities = changed_facilities.filter(
                ward__constituency__county_id=county)
            records = []
            for facility in facilities:
                latest_facility_change = FacilityUpgrade.objects.filter(
                    facility=facility)[0]
                data = {
                    "name": facility.name,
                    "code": facility.code,
                    "current_keph_level":
                        latest_facility_change.keph_level.name,
                    "previous_keph_level":
                        latest_facility_change.current_keph_level_name,
                    "previous_facility_type":
                        latest_facility_change.current_facility_type_name,
                    "current_facility_type":
                        latest_facility_change.facility_type.name,
                    "reason": latest_facility_change.reason.reason
                }
                records.append(data)

            return Response(data={
                "total_facilities_changed": len(facilities),
                "results": records
            })
