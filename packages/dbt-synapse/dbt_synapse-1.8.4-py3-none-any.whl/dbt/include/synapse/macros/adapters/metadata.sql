{%- macro synapse__get_use_database_sql(database) -%}
{%- endmacro -%}

{%- macro default__get_use_database_sql(database) -%}
  {{ return('') }}
{%- endmacro -%}

{% macro synapse__list_schemas(database) %}
  {% call statement('list_schemas', fetch_result=True, auto_begin=False) -%}
    select  name as [schema]
    from sys.schemas
  {% endcall %}
  {{ return(load_result('list_schemas').table) }}
{% endmacro %}

{% macro synapse__list_relations_without_caching(schema_relation) %}
  {% call statement('list_relations_without_caching', fetch_result=True) -%}
    {{ get_use_database_sql(schema_relation.database) }}
    select
      table_catalog as [database],
      table_name as [name],
      table_schema as [schema],
      case when table_type = 'BASE TABLE' then 'table'
           when table_type = 'VIEW' then 'view'
           else table_type
      end as table_type

    from INFORMATION_SCHEMA.TABLES
    where table_schema like '{{ schema_relation.schema }}'
      and table_catalog like '{{ schema_relation.database }}'
  {% endcall %}
  {{ return(load_result('list_relations_without_caching').table) }}
{% endmacro %}

{% macro synapse__get_relation_without_caching(schema_relation) -%}
  {% call statement('list_relations_without_caching', fetch_result=True) -%}
    {{ get_use_database_sql(schema_relation.database) }}
    select
      table_catalog as [database],
      table_name as [name],
      table_schema as [schema],
      case when table_type = 'BASE TABLE' then 'table'
           when table_type = 'VIEW' then 'view'
           else table_type
      end as table_type

    from INFORMATION_SCHEMA.TABLES {{ information_schema_hints() }}
    where table_schema like '{{ schema_relation.schema }}'
    and table_name like '{{ schema_relation.identifier }}'
  {% endcall %}
  {{ return(load_result('list_relations_without_caching').table) }}
{% endmacro %}
