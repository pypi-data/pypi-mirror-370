-- Need to check why model contract are not enforced.
-- TODO: Is it because Synapse uses Fabric table materialization and usage of this macro build model constraints?
{% macro synapse__create_table_as(temporary, relation, sql) -%}
    {%- set index = config.get('index', default="CLUSTERED COLUMNSTORE INDEX") -%}
    {%- set dist = config.get('dist', default="ROUND_ROBIN") -%}
    {% set tmp_relation = relation.incorporate(path={"identifier": relation.identifier ~ '__dbt_tmp_vw'}, type='view')-%}
    {%- set temp_view_sql = sql.replace("'", "''") -%}

    {{ get_create_view_as_sql(tmp_relation, sql) }}
    {% set contract_config = config.get('contract') %}

    {% if contract_config.enforced %}

        {{exceptions.warn("Model contracts cannot be enforced by <adapter>!")}}

        CREATE TABLE [{{relation.schema}}].[{{relation.identifier}}]
        {{ synapse__build_columns_constraints(tmp_relation) }}
        WITH(
            DISTRIBUTION = {{dist}},
            {{index}}
        )
        {{ get_assert_columns_equivalent(sql)  }}
        {% set listColumns %}
            {% for column in model['columns'] %}
                {{ "["~column~"]" }}{{ ", " if not loop.last }}
            {% endfor %}
        {%endset%}

        INSERT INTO [{{relation.schema}}].[{{relation.identifier}}]
        ({{listColumns}}) SELECT {{listColumns}} FROM [{{tmp_relation.schema}}].[{{tmp_relation.identifier}}]
    {%- else %}
        EXEC('CREATE TABLE [{{relation.database}}].[{{relation.schema}}].[{{relation.identifier}}]WITH(DISTRIBUTION = {{dist}},{{index}}) AS (SELECT * FROM [{{tmp_relation.database}}].[{{tmp_relation.schema}}].[{{tmp_relation.identifier}}]);');
    {% endif %}
    {% do adapter.drop_relation(tmp_relation)%}
{% endmacro %}
