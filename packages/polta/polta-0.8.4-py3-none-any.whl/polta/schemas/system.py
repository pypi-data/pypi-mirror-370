from deltalake import Field, Schema


file_history: Schema = Schema([
  Field('table_id', 'string'),
  Field('_file_path', 'string'),
  Field('_file_mod_ts', 'timestamp'),
  Field('_ingested_ts', 'timestamp')
])

pipe_history: Schema = Schema([
  Field('pipe_id', 'string'),
  Field('execution_start_ts', 'timestamp'),
  Field('execution_end_ts', 'timestamp'),
  Field('execution_duration', 'float'),
  Field('strict', 'boolean'),
  Field('succeeded', 'boolean'),
  Field('in_memory', 'boolean'),
  Field('total_count', 'long'),
  Field('passed_count', 'long'),
  Field('failed_count', 'long'),
  Field('quarantined_count', 'long')
])
