{% macro firebolt__get_materialized_view_configuration_changes(existing_relation, new_config) %}
    {{ exceptions.raise_compiler_error("Firebolt does not support materialized views") }}
{% endmacro %}
