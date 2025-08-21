# auto-generated file
import json
from cardinal_sdk.kotlin_types import symbols
from cardinal_sdk.model.CallResult import create_result_from_json, interpret_kt_error
from ctypes import cast, c_char_p
from cardinal_sdk.filters.FilterOptions import BaseFilterOptions, BaseSortableFilterOptions
from cardinal_sdk.model import Group


class GroupFilters:

	@classmethod
	def all(cls) -> BaseFilterOptions[Group]:
		call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.filters.GroupFilters.all(
		)
		result_info = create_result_from_json(cast(call_result, c_char_p).value.decode('utf-8'))
		symbols.DisposeString(call_result)
		if result_info.failure is not None:
			raise interpret_kt_error(result_info.failure)
		else:
			return_value = BaseFilterOptions(result_info.success)
			return return_value

	@classmethod
	def by_super_group(cls, super_group_id: str) -> BaseFilterOptions[Group]:
		payload = {
			"superGroupId": super_group_id,
		}
		call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.filters.GroupFilters.bySuperGroup(
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
	def with_content(cls, super_group_id: str, search_string: str) -> BaseSortableFilterOptions[Group]:
		payload = {
			"superGroupId": super_group_id,
			"searchString": search_string,
		}
		call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.filters.GroupFilters.withContent(
			json.dumps(payload).encode('utf-8')
		)
		result_info = create_result_from_json(cast(call_result, c_char_p).value.decode('utf-8'))
		symbols.DisposeString(call_result)
		if result_info.failure is not None:
			raise interpret_kt_error(result_info.failure)
		else:
			return_value = BaseSortableFilterOptions(result_info.success)
			return return_value
