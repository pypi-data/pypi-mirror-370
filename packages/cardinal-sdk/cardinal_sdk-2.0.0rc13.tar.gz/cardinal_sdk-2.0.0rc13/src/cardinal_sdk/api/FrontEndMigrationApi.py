# auto-generated file
import json
from cardinal_sdk.async_utils import execute_async_method_job
from cardinal_sdk.kotlin_types import symbols
from typing import Optional
from cardinal_sdk.model import FrontEndMigration, DocIdentifier
from cardinal_sdk.model.CallResult import create_result_from_json, interpret_kt_error
from ctypes import cast, c_char_p


class FrontEndMigrationApi:

	def __init__(self, cardinal_sdk):
		self.cardinal_sdk = cardinal_sdk

	async def get_front_end_migration_async(self, front_end_migration_id: str) -> Optional[FrontEndMigration]:
		def do_decode(raw_result):
			return FrontEndMigration._deserialize(raw_result) if raw_result is not None else None
		payload = {
			"frontEndMigrationId": front_end_migration_id,
		}
		return await execute_async_method_job(
			self.cardinal_sdk._executor,
			True,
			do_decode,
			symbols.kotlin.root.com.icure.cardinal.sdk.py.api.FrontEndMigrationApi.getFrontEndMigrationAsync,
			self.cardinal_sdk._native,
			json.dumps(payload).encode('utf-8'),
		)

	def get_front_end_migration_blocking(self, front_end_migration_id: str) -> Optional[FrontEndMigration]:
		payload = {
			"frontEndMigrationId": front_end_migration_id,
		}
		call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.api.FrontEndMigrationApi.getFrontEndMigrationBlocking(
			self.cardinal_sdk._native,
			json.dumps(payload).encode('utf-8'),
		)
		result_info = create_result_from_json(cast(call_result, c_char_p).value.decode('utf-8'))
		symbols.DisposeString(call_result)
		if result_info.failure is not None:
			raise interpret_kt_error(result_info.failure)
		else:
			return_value = FrontEndMigration._deserialize(result_info.success) if result_info.success is not None else None
			return return_value

	async def create_front_end_migration_async(self, front_end_migration: FrontEndMigration) -> FrontEndMigration:
		def do_decode(raw_result):
			return FrontEndMigration._deserialize(raw_result)
		payload = {
			"frontEndMigration": front_end_migration.__serialize__(),
		}
		return await execute_async_method_job(
			self.cardinal_sdk._executor,
			True,
			do_decode,
			symbols.kotlin.root.com.icure.cardinal.sdk.py.api.FrontEndMigrationApi.createFrontEndMigrationAsync,
			self.cardinal_sdk._native,
			json.dumps(payload).encode('utf-8'),
		)

	def create_front_end_migration_blocking(self, front_end_migration: FrontEndMigration) -> FrontEndMigration:
		payload = {
			"frontEndMigration": front_end_migration.__serialize__(),
		}
		call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.api.FrontEndMigrationApi.createFrontEndMigrationBlocking(
			self.cardinal_sdk._native,
			json.dumps(payload).encode('utf-8'),
		)
		result_info = create_result_from_json(cast(call_result, c_char_p).value.decode('utf-8'))
		symbols.DisposeString(call_result)
		if result_info.failure is not None:
			raise interpret_kt_error(result_info.failure)
		else:
			return_value = FrontEndMigration._deserialize(result_info.success)
			return return_value

	async def get_front_end_migrations_async(self) -> list[FrontEndMigration]:
		def do_decode(raw_result):
			return [FrontEndMigration._deserialize(x1) for x1 in raw_result]
		return await execute_async_method_job(
			self.cardinal_sdk._executor,
			True,
			do_decode,
			symbols.kotlin.root.com.icure.cardinal.sdk.py.api.FrontEndMigrationApi.getFrontEndMigrationsAsync,
			self.cardinal_sdk._native,
		)

	def get_front_end_migrations_blocking(self) -> list[FrontEndMigration]:
		call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.api.FrontEndMigrationApi.getFrontEndMigrationsBlocking(
			self.cardinal_sdk._native,
		)
		result_info = create_result_from_json(cast(call_result, c_char_p).value.decode('utf-8'))
		symbols.DisposeString(call_result)
		if result_info.failure is not None:
			raise interpret_kt_error(result_info.failure)
		else:
			return_value = [FrontEndMigration._deserialize(x1) for x1 in result_info.success]
			return return_value

	async def delete_front_end_migration_async(self, front_end_migration_id: str) -> DocIdentifier:
		def do_decode(raw_result):
			return DocIdentifier._deserialize(raw_result)
		payload = {
			"frontEndMigrationId": front_end_migration_id,
		}
		return await execute_async_method_job(
			self.cardinal_sdk._executor,
			True,
			do_decode,
			symbols.kotlin.root.com.icure.cardinal.sdk.py.api.FrontEndMigrationApi.deleteFrontEndMigrationAsync,
			self.cardinal_sdk._native,
			json.dumps(payload).encode('utf-8'),
		)

	def delete_front_end_migration_blocking(self, front_end_migration_id: str) -> DocIdentifier:
		payload = {
			"frontEndMigrationId": front_end_migration_id,
		}
		call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.api.FrontEndMigrationApi.deleteFrontEndMigrationBlocking(
			self.cardinal_sdk._native,
			json.dumps(payload).encode('utf-8'),
		)
		result_info = create_result_from_json(cast(call_result, c_char_p).value.decode('utf-8'))
		symbols.DisposeString(call_result)
		if result_info.failure is not None:
			raise interpret_kt_error(result_info.failure)
		else:
			return_value = DocIdentifier._deserialize(result_info.success)
			return return_value

	async def get_front_end_migration_by_name_async(self, front_end_migration_name: str) -> list[FrontEndMigration]:
		def do_decode(raw_result):
			return [FrontEndMigration._deserialize(x1) for x1 in raw_result]
		payload = {
			"frontEndMigrationName": front_end_migration_name,
		}
		return await execute_async_method_job(
			self.cardinal_sdk._executor,
			True,
			do_decode,
			symbols.kotlin.root.com.icure.cardinal.sdk.py.api.FrontEndMigrationApi.getFrontEndMigrationByNameAsync,
			self.cardinal_sdk._native,
			json.dumps(payload).encode('utf-8'),
		)

	def get_front_end_migration_by_name_blocking(self, front_end_migration_name: str) -> list[FrontEndMigration]:
		payload = {
			"frontEndMigrationName": front_end_migration_name,
		}
		call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.api.FrontEndMigrationApi.getFrontEndMigrationByNameBlocking(
			self.cardinal_sdk._native,
			json.dumps(payload).encode('utf-8'),
		)
		result_info = create_result_from_json(cast(call_result, c_char_p).value.decode('utf-8'))
		symbols.DisposeString(call_result)
		if result_info.failure is not None:
			raise interpret_kt_error(result_info.failure)
		else:
			return_value = [FrontEndMigration._deserialize(x1) for x1 in result_info.success]
			return return_value

	async def modify_front_end_migration_async(self, front_end_migration: FrontEndMigration) -> FrontEndMigration:
		def do_decode(raw_result):
			return FrontEndMigration._deserialize(raw_result)
		payload = {
			"frontEndMigration": front_end_migration.__serialize__(),
		}
		return await execute_async_method_job(
			self.cardinal_sdk._executor,
			True,
			do_decode,
			symbols.kotlin.root.com.icure.cardinal.sdk.py.api.FrontEndMigrationApi.modifyFrontEndMigrationAsync,
			self.cardinal_sdk._native,
			json.dumps(payload).encode('utf-8'),
		)

	def modify_front_end_migration_blocking(self, front_end_migration: FrontEndMigration) -> FrontEndMigration:
		payload = {
			"frontEndMigration": front_end_migration.__serialize__(),
		}
		call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.api.FrontEndMigrationApi.modifyFrontEndMigrationBlocking(
			self.cardinal_sdk._native,
			json.dumps(payload).encode('utf-8'),
		)
		result_info = create_result_from_json(cast(call_result, c_char_p).value.decode('utf-8'))
		symbols.DisposeString(call_result)
		if result_info.failure is not None:
			raise interpret_kt_error(result_info.failure)
		else:
			return_value = FrontEndMigration._deserialize(result_info.success)
			return return_value
