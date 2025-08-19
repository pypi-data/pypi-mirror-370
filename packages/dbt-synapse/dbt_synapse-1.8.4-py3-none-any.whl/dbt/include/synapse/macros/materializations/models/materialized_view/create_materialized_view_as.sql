{% macro synapse__get_replace_materialized_view_as_sql(relation, sql, existing_relation, backup_relation, intermediate_relation) %}
    {# Synapse does not have ALTER...RENAME function, so use synapse__rename_relation_script #}

    {%- set dist = config.get('dist', default="ROUND_ROBIN") -%}
    EXEC('
    CREATE materialized view [{{intermediate_relation.schema}}].[{{intermediate_relation.identifier}}]
    WITH ( DISTRIBUTION = {{dist}} )
    AS {{ sql }}
    ');

    {{ synapse__rename_relation_script(existing_relation, backup_relation) }}
    {{ synapse__rename_relation_script(intermediate_relation, relation) }}

{% endmacro %}

{% macro synapse__get_create_materialized_view_as_sql(relation, sql) %}
    {%- set dist = config.get('dist', default="ROUND_ROBIN") -%}

    CREATE materialized view [{{relation.schema}}].[{{relation.identifier}}]
    WITH ( DISTRIBUTION = {{dist}} )
    AS {{ sql }}

{% endmacro %}
