{% from 'copier_macro.sql' import copy_into %}
{{ copy_into(destination_stage, source, materialization_schema, cast_types) }}
