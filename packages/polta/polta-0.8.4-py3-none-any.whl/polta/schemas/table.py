from deltalake import Field, Schema


raw_metadata: Schema = Schema([
  Field('_raw_id', 'string'),
  Field('_ingested_ts', 'timestamp'),
  Field('_file_path', 'string'),
  Field('_file_name', 'string'),
  Field('_file_mod_ts', 'timestamp')
])

conformed_metadata: Schema = Schema([
  Field('_raw_id', 'string'),
  Field('_conformed_id', 'string'),
  Field('_conformed_ts', 'timestamp'),
  Field('_ingested_ts', 'timestamp'),
  Field('_file_path', 'string'),
  Field('_file_name', 'string'),
  Field('_file_mod_ts', 'timestamp')
])

canonical_metadata: Schema = Schema([
  Field('_raw_id', 'string'),
  Field('_conformed_id', 'string'),
  Field('_canonicalized_id', 'string'),
  Field('_created_ts', 'timestamp'),
  Field('_modified_ts', 'timestamp')
])

standard_metadata: Schema = Schema([
  Field('_id', 'string'),
  Field('_created_ts', 'timestamp'),
  Field('_modified_ts', 'timestamp')
])

failed_test: Schema = Schema([
  Field('failed_test', 'string')
])
