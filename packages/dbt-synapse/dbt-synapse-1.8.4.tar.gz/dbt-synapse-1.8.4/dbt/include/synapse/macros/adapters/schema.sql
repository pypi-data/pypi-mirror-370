{% macro synapse__create_schema(relation) -%}
  {% call statement('create_schema') -%}
    IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = '{{ relation.without_identifier().schema }}')
    BEGIN
    EXEC('CREATE SCHEMA [{{ relation.without_identifier().schema }}]')
    END
  {% endcall %}
{% endmacro %}

{% macro synapse__create_schema_with_authorization(relation, schema_authorization) -%}
  {% call statement('create_schema') -%}
    
    IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = '{{ relation.schema }}')
    BEGIN
    EXEC('CREATE SCHEMA [{{ relation.schema }}] AUTHORIZATION [{{ schema_authorization }}]')
    END
  {% endcall %}
{% endmacro %}

{% macro synapse__drop_schema(relation) -%}
  {%- set relations_in_schema = list_relations_without_caching(relation) %}

  {% for row in relations_in_schema %}
    {%- set schema_relation = api.Relation.create(database=relation.database,
                                               schema=relation.schema,
                                               identifier=row[1],
                                               type=row[3]
                                               ) -%}
    {% do adapter.drop_relation(schema_relation) %}
  {%- endfor %}

  {% call statement('drop_schema') -%}
    IF EXISTS (SELECT * FROM sys.schemas WHERE name = '{{ relation.without_identifier().schema }}')
    BEGIN
    EXEC('DROP SCHEMA [{{ relation.without_identifier().schema }}]')
    END
  {% endcall %}
{% endmacro %}
