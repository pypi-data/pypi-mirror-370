# auto-generated file
import json
from cardinal_sdk.kotlin_types import symbols
from cardinal_sdk.model.CallResult import create_result_from_json, interpret_kt_error
from ctypes import cast, c_char_p
from cardinal_sdk.filters.FilterOptions import BaseFilterOptions, FilterOptions, BaseSortableFilterOptions, SortableFilterOptions
from cardinal_sdk.model import Service, Identifier, Patient, serialize_patient, LinkQualification
from typing import Optional


class ServiceFilters:

	@classmethod
	def all_services_for_data_owner(cls, data_owner_id: str) -> BaseFilterOptions[Service]:
		payload = {
			"dataOwnerId": data_owner_id,
		}
		call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.filters.ServiceFilters.allServicesForDataOwner(
			json.dumps(payload).encode('utf-8')
		)
		result_info = create_result_from_json(cast(call_result, c_char_p).value.decode('utf-8'))
		symbols.DisposeString(call_result)
		if result_info.failure is not None:
			raise interpret_kt_error(result_info.failure)
		else:
			return_value = BaseFilterOptions(result_info.success)
			return return_value

	@classmethod
	def all_services_for_self(cls) -> FilterOptions[Service]:
		call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.filters.ServiceFilters.allServicesForSelf(
		)
		result_info = create_result_from_json(cast(call_result, c_char_p).value.decode('utf-8'))
		symbols.DisposeString(call_result)
		if result_info.failure is not None:
			raise interpret_kt_error(result_info.failure)
		else:
			return_value = FilterOptions(result_info.success)
			return return_value

	@classmethod
	def by_identifiers_for_data_owner(cls, data_owner_id: str, identifiers: list[Identifier]) -> BaseSortableFilterOptions[Service]:
		payload = {
			"dataOwnerId": data_owner_id,
			"identifiers": [x0.__serialize__() for x0 in identifiers],
		}
		call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.filters.ServiceFilters.byIdentifiersForDataOwner(
			json.dumps(payload).encode('utf-8')
		)
		result_info = create_result_from_json(cast(call_result, c_char_p).value.decode('utf-8'))
		symbols.DisposeString(call_result)
		if result_info.failure is not None:
			raise interpret_kt_error(result_info.failure)
		else:
			return_value = BaseSortableFilterOptions(result_info.success)
			return return_value

	@classmethod
	def by_code_and_value_date_for_data_owner(cls, data_owner_id: str, code_type: str, code_code: Optional[str] = None, start_of_service_value_date: Optional[int] = None, end_of_service_value_date: Optional[int] = None) -> BaseSortableFilterOptions[Service]:
		payload = {
			"dataOwnerId": data_owner_id,
			"codeType": code_type,
			"codeCode": code_code,
			"startOfServiceValueDate": start_of_service_value_date,
			"endOfServiceValueDate": end_of_service_value_date,
		}
		call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.filters.ServiceFilters.byCodeAndValueDateForDataOwner(
			json.dumps(payload).encode('utf-8')
		)
		result_info = create_result_from_json(cast(call_result, c_char_p).value.decode('utf-8'))
		symbols.DisposeString(call_result)
		if result_info.failure is not None:
			raise interpret_kt_error(result_info.failure)
		else:
			return_value = BaseSortableFilterOptions(result_info.success)
			return return_value

	@classmethod
	def by_tag_and_value_date_for_data_owner(cls, data_owner_id: str, tag_type: str, tag_code: Optional[str] = None, start_of_service_value_date: Optional[int] = None, end_of_service_value_date: Optional[int] = None) -> BaseSortableFilterOptions[Service]:
		payload = {
			"dataOwnerId": data_owner_id,
			"tagType": tag_type,
			"tagCode": tag_code,
			"startOfServiceValueDate": start_of_service_value_date,
			"endOfServiceValueDate": end_of_service_value_date,
		}
		call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.filters.ServiceFilters.byTagAndValueDateForDataOwner(
			json.dumps(payload).encode('utf-8')
		)
		result_info = create_result_from_json(cast(call_result, c_char_p).value.decode('utf-8'))
		symbols.DisposeString(call_result)
		if result_info.failure is not None:
			raise interpret_kt_error(result_info.failure)
		else:
			return_value = BaseSortableFilterOptions(result_info.success)
			return return_value

	@classmethod
	def by_patients_for_data_owner(cls, data_owner_id: str, patients: list[Patient]) -> SortableFilterOptions[Service]:
		payload = {
			"dataOwnerId": data_owner_id,
			"patients": [serialize_patient(x0) for x0 in patients],
		}
		call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.filters.ServiceFilters.byPatientsForDataOwner(
			json.dumps(payload).encode('utf-8')
		)
		result_info = create_result_from_json(cast(call_result, c_char_p).value.decode('utf-8'))
		symbols.DisposeString(call_result)
		if result_info.failure is not None:
			raise interpret_kt_error(result_info.failure)
		else:
			return_value = SortableFilterOptions(result_info.success)
			return return_value

	@classmethod
	def by_patients_secret_ids_for_data_owner(cls, data_owner_id: str, secret_ids: list[str]) -> BaseSortableFilterOptions[Service]:
		payload = {
			"dataOwnerId": data_owner_id,
			"secretIds": [x0 for x0 in secret_ids],
		}
		call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.filters.ServiceFilters.byPatientsSecretIdsForDataOwner(
			json.dumps(payload).encode('utf-8')
		)
		result_info = create_result_from_json(cast(call_result, c_char_p).value.decode('utf-8'))
		symbols.DisposeString(call_result)
		if result_info.failure is not None:
			raise interpret_kt_error(result_info.failure)
		else:
			return_value = BaseSortableFilterOptions(result_info.success)
			return return_value

	@classmethod
	def by_health_element_id_from_sub_contact_for_data_owner(cls, data_owner_id: str, health_element_ids: list[str]) -> BaseSortableFilterOptions[Service]:
		payload = {
			"dataOwnerId": data_owner_id,
			"healthElementIds": [x0 for x0 in health_element_ids],
		}
		call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.filters.ServiceFilters.byHealthElementIdFromSubContactForDataOwner(
			json.dumps(payload).encode('utf-8')
		)
		result_info = create_result_from_json(cast(call_result, c_char_p).value.decode('utf-8'))
		symbols.DisposeString(call_result)
		if result_info.failure is not None:
			raise interpret_kt_error(result_info.failure)
		else:
			return_value = BaseSortableFilterOptions(result_info.success)
			return return_value

	@classmethod
	def by_identifiers_for_self(cls, identifiers: list[Identifier]) -> SortableFilterOptions[Service]:
		payload = {
			"identifiers": [x0.__serialize__() for x0 in identifiers],
		}
		call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.filters.ServiceFilters.byIdentifiersForSelf(
			json.dumps(payload).encode('utf-8')
		)
		result_info = create_result_from_json(cast(call_result, c_char_p).value.decode('utf-8'))
		symbols.DisposeString(call_result)
		if result_info.failure is not None:
			raise interpret_kt_error(result_info.failure)
		else:
			return_value = SortableFilterOptions(result_info.success)
			return return_value

	@classmethod
	def by_code_and_value_date_for_self(cls, code_type: str, code_code: Optional[str] = None, start_of_service_value_date: Optional[int] = None, end_of_service_value_date: Optional[int] = None) -> SortableFilterOptions[Service]:
		payload = {
			"codeType": code_type,
			"codeCode": code_code,
			"startOfServiceValueDate": start_of_service_value_date,
			"endOfServiceValueDate": end_of_service_value_date,
		}
		call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.filters.ServiceFilters.byCodeAndValueDateForSelf(
			json.dumps(payload).encode('utf-8')
		)
		result_info = create_result_from_json(cast(call_result, c_char_p).value.decode('utf-8'))
		symbols.DisposeString(call_result)
		if result_info.failure is not None:
			raise interpret_kt_error(result_info.failure)
		else:
			return_value = SortableFilterOptions(result_info.success)
			return return_value

	@classmethod
	def by_tag_and_value_date_for_self(cls, tag_type: str, tag_code: Optional[str] = None, start_of_service_value_date: Optional[int] = None, end_of_service_value_date: Optional[int] = None) -> SortableFilterOptions[Service]:
		payload = {
			"tagType": tag_type,
			"tagCode": tag_code,
			"startOfServiceValueDate": start_of_service_value_date,
			"endOfServiceValueDate": end_of_service_value_date,
		}
		call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.filters.ServiceFilters.byTagAndValueDateForSelf(
			json.dumps(payload).encode('utf-8')
		)
		result_info = create_result_from_json(cast(call_result, c_char_p).value.decode('utf-8'))
		symbols.DisposeString(call_result)
		if result_info.failure is not None:
			raise interpret_kt_error(result_info.failure)
		else:
			return_value = SortableFilterOptions(result_info.success)
			return return_value

	@classmethod
	def by_patients_for_self(cls, patients: list[Patient]) -> SortableFilterOptions[Service]:
		payload = {
			"patients": [serialize_patient(x0) for x0 in patients],
		}
		call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.filters.ServiceFilters.byPatientsForSelf(
			json.dumps(payload).encode('utf-8')
		)
		result_info = create_result_from_json(cast(call_result, c_char_p).value.decode('utf-8'))
		symbols.DisposeString(call_result)
		if result_info.failure is not None:
			raise interpret_kt_error(result_info.failure)
		else:
			return_value = SortableFilterOptions(result_info.success)
			return return_value

	@classmethod
	def by_patients_secret_ids_for_self(cls, secret_ids: list[str]) -> SortableFilterOptions[Service]:
		payload = {
			"secretIds": [x0 for x0 in secret_ids],
		}
		call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.filters.ServiceFilters.byPatientsSecretIdsForSelf(
			json.dumps(payload).encode('utf-8')
		)
		result_info = create_result_from_json(cast(call_result, c_char_p).value.decode('utf-8'))
		symbols.DisposeString(call_result)
		if result_info.failure is not None:
			raise interpret_kt_error(result_info.failure)
		else:
			return_value = SortableFilterOptions(result_info.success)
			return return_value

	@classmethod
	def by_health_element_id_from_sub_contact_for_self(cls, health_element_ids: list[str]) -> SortableFilterOptions[Service]:
		payload = {
			"healthElementIds": [x0 for x0 in health_element_ids],
		}
		call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.filters.ServiceFilters.byHealthElementIdFromSubContactForSelf(
			json.dumps(payload).encode('utf-8')
		)
		result_info = create_result_from_json(cast(call_result, c_char_p).value.decode('utf-8'))
		symbols.DisposeString(call_result)
		if result_info.failure is not None:
			raise interpret_kt_error(result_info.failure)
		else:
			return_value = SortableFilterOptions(result_info.success)
			return return_value

	@classmethod
	def by_ids(cls, ids: list[str]) -> BaseSortableFilterOptions[Service]:
		payload = {
			"ids": [x0 for x0 in ids],
		}
		call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.filters.ServiceFilters.byIds(
			json.dumps(payload).encode('utf-8')
		)
		result_info = create_result_from_json(cast(call_result, c_char_p).value.decode('utf-8'))
		symbols.DisposeString(call_result)
		if result_info.failure is not None:
			raise interpret_kt_error(result_info.failure)
		else:
			return_value = BaseSortableFilterOptions(result_info.success)
			return return_value

	@classmethod
	def by_association_id(cls, association_id: str) -> BaseFilterOptions[Service]:
		payload = {
			"associationId": association_id,
		}
		call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.filters.ServiceFilters.byAssociationId(
			json.dumps(payload).encode('utf-8')
		)
		result_info = create_result_from_json(cast(call_result, c_char_p).value.decode('utf-8'))
		symbols.DisposeString(call_result)
		if result_info.failure is not None:
			raise interpret_kt_error(result_info.failure)
		else:
			return_value = BaseFilterOptions(result_info.success)
			return return_value

	@classmethod
	def by_qualified_link(cls, link_values: list[str], link_qualification: Optional[LinkQualification] = None) -> BaseFilterOptions[Service]:
		payload = {
			"linkValues": [x0 for x0 in link_values],
			"linkQualification": link_qualification.__serialize__() if link_qualification is not None else None,
		}
		call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.filters.ServiceFilters.byQualifiedLink(
			json.dumps(payload).encode('utf-8')
		)
		result_info = create_result_from_json(cast(call_result, c_char_p).value.decode('utf-8'))
		symbols.DisposeString(call_result)
		if result_info.failure is not None:
			raise interpret_kt_error(result_info.failure)
		else:
			return_value = BaseFilterOptions(result_info.success)
			return return_value

	@classmethod
	def by_patients_date_for_data_owner(cls, data_owner_id: str, patients: list[Patient], from_: Optional[int] = None, to: Optional[int] = None, descending: bool = False) -> SortableFilterOptions[Service]:
		payload = {
			"dataOwnerId": data_owner_id,
			"patients": [serialize_patient(x0) for x0 in patients],
			"from": from_,
			"to": to,
			"descending": descending,
		}
		call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.filters.ServiceFilters.byPatientsDateForDataOwner(
			json.dumps(payload).encode('utf-8')
		)
		result_info = create_result_from_json(cast(call_result, c_char_p).value.decode('utf-8'))
		symbols.DisposeString(call_result)
		if result_info.failure is not None:
			raise interpret_kt_error(result_info.failure)
		else:
			return_value = SortableFilterOptions(result_info.success)
			return return_value

	@classmethod
	def by_patients_date_for_self(cls, patients: list[Patient], from_: Optional[int] = None, to: Optional[int] = None, descending: bool = False) -> SortableFilterOptions[Service]:
		payload = {
			"patients": [serialize_patient(x0) for x0 in patients],
			"from": from_,
			"to": to,
			"descending": descending,
		}
		call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.filters.ServiceFilters.byPatientsDateForSelf(
			json.dumps(payload).encode('utf-8')
		)
		result_info = create_result_from_json(cast(call_result, c_char_p).value.decode('utf-8'))
		symbols.DisposeString(call_result)
		if result_info.failure is not None:
			raise interpret_kt_error(result_info.failure)
		else:
			return_value = SortableFilterOptions(result_info.success)
			return return_value

	@classmethod
	def by_patient_secret_ids_date_for_data_owner(cls, data_owner_id: str, secret_ids: list[str], from_: Optional[int] = None, to: Optional[int] = None, descending: bool = False) -> BaseSortableFilterOptions[Service]:
		payload = {
			"dataOwnerId": data_owner_id,
			"secretIds": [x0 for x0 in secret_ids],
			"from": from_,
			"to": to,
			"descending": descending,
		}
		call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.filters.ServiceFilters.byPatientSecretIdsDateForDataOwner(
			json.dumps(payload).encode('utf-8')
		)
		result_info = create_result_from_json(cast(call_result, c_char_p).value.decode('utf-8'))
		symbols.DisposeString(call_result)
		if result_info.failure is not None:
			raise interpret_kt_error(result_info.failure)
		else:
			return_value = BaseSortableFilterOptions(result_info.success)
			return return_value

	@classmethod
	def by_patient_secret_ids_date_for_self(cls, secret_ids: list[str], from_: Optional[int] = None, to: Optional[int] = None, descending: bool = False) -> SortableFilterOptions[Service]:
		payload = {
			"secretIds": [x0 for x0 in secret_ids],
			"from": from_,
			"to": to,
			"descending": descending,
		}
		call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.filters.ServiceFilters.byPatientSecretIdsDateForSelf(
			json.dumps(payload).encode('utf-8')
		)
		result_info = create_result_from_json(cast(call_result, c_char_p).value.decode('utf-8'))
		symbols.DisposeString(call_result)
		if result_info.failure is not None:
			raise interpret_kt_error(result_info.failure)
		else:
			return_value = SortableFilterOptions(result_info.success)
			return return_value
