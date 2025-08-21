{#- attribute.rst - Intelligent attribute template with extension integration -#}
{%- extends "python/_base/foundation.j2" -%}

{#- Import components -#}
{%- import "python/_components/code_blocks.j2" as code with context -%}

{%- block signature -%}
.. py:attribute:: {{ obj.name }}
{%- if obj.annotation %}{{ '\n' }}   :type: {{ obj.annotation }}{% endif %}
{%- if obj.value %}{{ '\n' }}   :value: {{ obj.value|truncate(100) }}{% endif %}

{%- if obj.docstring %}
   {{ obj.docstring|indent(3) }}
{%- endif %}
{%- endblock signature -%}

{%- block content -%}
{#- Attribute metadata -#}
{%- if has_design and (obj.annotation or obj.value or obj.is_class_attribute) %}
.. grid:: 1 1 2 3
   :gutter: 2
   :margin: 0 0 3 0

   {%- if obj.annotation %}
   {{ info_card('Type', '``' ~ code.format_type(obj.annotation) ~ '``', {'columns': '12 6 4 4'}) }}
   {%- endif %}
   
   {%- if obj.value %}
   {{ info_card('Default Value', render_attribute_value(obj.value), {'columns': '12 6 4 4'}) }}
   {%- endif %}
   
   {%- if obj.is_class_attribute %}
   {{ info_card('Scope', 'Class Attribute', {'columns': '12 12 4 4', 'color': 'info'}) }}
   {%- else %}
   {{ info_card('Scope', 'Instance Attribute', {'columns': '12 12 4 4', 'color': 'success'}) }}
   {%- endif %}
{%- endif %}

{#- Detailed type information -#}
{%- if obj.annotation and is_complex_type(obj.annotation) %}

Type Details
------------

{%- if has_mermaid %}
{{ render_type_diagram(obj.annotation) }}
{%- else %}
``{{ obj.annotation }}``
{%- endif %}
{%- endif %}

{#- Validation rules (for Pydantic fields) -#}
{%- if obj.validators %}

Validation Rules
----------------

{%- for validator in obj.validators %}
{%- if has_design %}
.. admonition:: {{ validator.name }}
   :class: tip

   {{ validator.description }}
   
   {%- if validator.code %}
   .. code-block:: python
      
      {{ validator.code|indent(6) }}
   {%- endif %}
{%- else %}
**{{ validator.name }}**: {{ validator.description }}
{%- endif %}
{%- endfor %}
{%- endif %}

{#- Constraints (for Pydantic fields) -#}
{%- if obj.constraints %}

Constraints
-----------

.. list-table::
   :header-rows: 1
   
   * - Constraint
     - Value
   {%- for constraint, value in obj.constraints.items() %}
   * - {{ constraint }}
     - ``{{ value }}``
   {%- endfor %}
{%- endif %}

{#- Usage examples -#}
{%- if obj.examples %}

Usage Examples
--------------

{%- for example in obj.examples %}
{{ code.render_code_block(example) }}
{%- endfor %}
{%- endif %}

{#- Related attributes -#}
{%- if obj.related_attributes %}

Related Attributes
------------------

{%- for attr in obj.related_attributes %}
* :attr:`{{ attr }}` -- {{ get_attribute_summary(attr) }}
{%- endfor %}
{%- endif %}

{#- Mutation warning for mutable defaults -#}
{%- if is_mutable_default(obj.value) %}

.. warning::
   
   This attribute has a mutable default value. Be careful not to modify
   the default value directly as it will affect all instances.
{%- endif %}
{%- endblock content -%}

{#- Helper macros -#}
{%- macro render_attribute_value(value) -%}
{%- if value is string and value|length > 50 %}
.. code-block:: python
   
   {{ value|truncate(200) }}
{%- elif value is mapping %}
.. code-block:: python
   
   {{ value|pprint|truncate(200) }}
{%- elif value is iterable and value is not string %}
.. code-block:: python
   
   {{ value|list|truncate(200) }}
{%- else %}
``{{ value }}``
{%- endif %}
{%- endmacro -%}

{%- macro is_complex_type(annotation) -%}
{#- Check if type annotation is complex enough to warrant detailed display -#}
{{ 'Union' in annotation or 'Optional' in annotation or 'List' in annotation or 'Dict' in annotation }}
{%- endmacro -%}

{%- macro render_type_diagram(annotation) -%}
{#- Render a type hierarchy diagram for complex types -#}
.. mermaid::
   
   graph LR
   A[{{ obj.name }}] --> B[{{ annotation }}]
{%- endmacro -%}

{%- macro is_mutable_default(value) -%}
{#- Check if default value is mutable -#}
{{ value is mapping or (value is iterable and value is not string) }}
{%- endmacro -%}

{%- macro get_attribute_summary(attr_name) -%}
Related attribute description
{%- endmacro -%}