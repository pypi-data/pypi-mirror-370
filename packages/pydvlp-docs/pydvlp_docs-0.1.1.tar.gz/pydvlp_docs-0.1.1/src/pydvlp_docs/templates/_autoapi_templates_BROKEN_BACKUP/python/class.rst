{#- class.rst - Intelligent class template with all extension integration -#}
{%- extends "python/_base/progressive.j2" -%}

{#- Import component macros -#}
{%- import "python/_components/diagrams.j2" as diagrams with context -%}
{%- import "python/_components/code_blocks.j2" as code with context -%}
{%- import "python/_components/tooltips.j2" as tooltips with context -%}
{%- import "python/_macros/type_specific.j2" as types with context -%}

{#- Detect class type for intelligent rendering -#}
{%- set base_names = obj.bases|map(attribute='name')|list if obj.bases else [] -%}
{%- set is_pydantic = 'BaseModel' in base_names or 'pydantic' in obj.module|default('') -%}
{%- set is_agent = 'Agent' in base_names or 'BaseAgent' in base_names -%}
{%- set is_tool = 'Tool' in base_names or 'BaseTool' in base_names -%}
{%- set is_enum = 'Enum' in base_names or 'IntEnum' in base_names or 'StrEnum' in base_names -%}
{%- set is_exception = 'Exception' in base_names or 'Error' in base_names -%}
{%- set is_dataclass = obj.dataclass|default(false) or '@dataclass' in obj.raw_docstring|default('') -%}

{%- block signature -%}
.. py:{{ obj.type }}:: {{ obj.name }}
{%- if obj.args %}({{ obj.args|join(', ') }}){% endif %}
{%- if obj.module %}{{ '\n' }}   :module: {{ obj.module }}{% endif %}
{%- if is_pydantic %}{{ '\n' }}   :canonical: {{ obj.module }}.{{ obj.name }}{% endif %}

{%- if obj.docstring %}
   {{ obj.docstring|indent(3) }}
{%- endif %}
{%- endblock signature -%}

{%- block content -%}
{#- Visual class diagram if extensions available -#}
{%- if obj.bases or obj.subclasses %}
{{ diagrams.render_class_hierarchy(obj) }}
{%- endif %}

{#- Quick overview section with cards -#}
{%- if has_design %}
.. grid:: 1 1 2 3
   :gutter: 3
   :margin: 4 4 0 0

   {{ info_card('Quick Info', get_quick_info(obj), {'columns': '12 12 6 4'}) }}
   
   {%- if is_pydantic %}
   {{ info_card('Schema', get_pydantic_schema_preview(obj), {'columns': '12 12 6 4', 'color': 'info'}) }}
   {%- elif is_agent %}
   {{ info_card('Agent Config', get_agent_config(obj), {'columns': '12 12 6 4', 'color': 'success'}) }}
   {%- endif %}
   
   {%- if obj.examples %}
   {{ info_card('Quick Example', obj.examples[0] if obj.examples else '', {'columns': '12 12 12 4', 'color': 'primary'}) }}
   {%- endif %}
{%- endif %}

{#- Type-specific rendering -#}
{%- if is_pydantic %}
{{ types.render_pydantic_model(obj) }}
{%- elif is_agent %}
{{ types.render_agent_class(obj) }}
{%- elif is_tool %}
{{ types.render_tool_class(obj) }}
{%- elif is_enum %}
{{ types.render_enum_class(obj) }}
{%- elif is_exception %}
{{ types.render_exception_class(obj) }}
{%- elif is_dataclass %}
{{ types.render_dataclass(obj) }}
{%- endif %}

{#- Constructor/Initialization -#}
{%- if obj.args and obj.args != ['self'] %}
{{ progressive_section('Constructor', render_constructor(obj), {'open': true, 'icon': '🔧'}) }}
{%- endif %}

{#- Class attributes and properties -#}
{%- if obj.class_attributes or obj.attributes %}
{{ progressive_section('Attributes ' + object_stats({'all_attributes': obj.attributes}), 
                      render_attributes_section(obj), 
                      {'open': false, 'icon': '📊'}) }}
{%- endif %}

{#- Methods section with smart grouping -#}
{%- if obj.methods %}
{%- set public_methods = obj.methods|selectattr('name', 'match', '^[^_]')|list -%}
{%- set private_methods = obj.methods|selectattr('name', 'match', '^_[^_]')|list -%}
{%- set dunder_methods = obj.methods|selectattr('name', 'match', '^__')|list -%}

{{ progressive_section('Methods ' + object_stats({'all_methods': obj.methods}), 
                      render_methods_tabbed(public_methods, private_methods, dunder_methods), 
                      {'open': true, 'icon': '⚡'}) }}
{%- endif %}

{#- Inheritance details -#}
{%- if obj.bases and has_design %}
{{ progressive_section('Inheritance Details', 
                      render_inheritance_details(obj), 
                      {'open': false, 'icon': '🏗️'}) }}
{%- endif %}

{#- Usage examples with tabs -#}
{%- if obj.examples and obj.examples|length > 1 %}
{{ progressive_section('Examples', 
                      render_examples_tabbed(obj.examples), 
                      {'open': true, 'icon': '📚'}) }}
{%- endif %}

{#- Source code viewer -#}
{%- if obj.source and has_copybutton %}
{{ progressive_section('Source Code', 
                      code.render_source_code(obj), 
                      {'open': false, 'icon': '📝'}) }}
{%- endif %}
{%- endblock content -%}

{#- Helper functions -#}
{%- macro get_quick_info(obj) -%}
**Type**: ``{{ obj.type }}``

{%- if obj.bases %}
**Inherits**: {% for base in obj.bases %}`{{ base.name }}`{% if not loop.last %}, {% endif %}{% endfor %}
{%- endif %}

{%- if obj.subclasses %}
**Subclassed by**: {{ obj.subclasses|length }} classes
{%- endif %}

{%- if obj.abstract %}
**Abstract**: This is an abstract base class
{%- endif %}

{%- if obj.final %}
**Final**: This class cannot be subclassed
{%- endif %}
{%- endmacro -%}

{%- macro get_pydantic_schema_preview(obj) -%}
{%- if has_copybutton %}
.. code-block:: json
   :class: copybutton
   
   {
     "title": "{{ obj.name }}",
     "type": "object",
     "properties": {
       // {{ obj.attributes|length|default(0) }} fields
     }
   }
{%- else %}
View the full schema in the Fields section below.
{%- endif %}
{%- endmacro -%}

{%- macro get_agent_config(obj) -%}
{%- if obj.methods %}
{%- set tool_methods = obj.methods|selectattr('name', 'match', 'tool_')|list -%}
**Tools**: {{ tool_methods|length }} available
{%- endif %}

**Agent Type**: {{ obj.name }}

{%- if 'async' in obj.raw_docstring|default('')|lower %}
**Async**: ✓ Supports async execution
{%- endif %}
{%- endmacro -%}

{%- macro render_constructor(obj) -%}
{%- if has_design %}
.. code-block:: python
   {%- if has_copybutton %}
   :class: copybutton
   {%- endif %}
   
   {{ obj.name }}(
   {%- for arg in obj.args if arg != 'self' %}
       {{ arg }},
   {%- endfor %}
   )
{%- endif %}

{%- if obj.parameters %}
**Parameters:**

{%- for param in obj.parameters %}
* **{{ param.name }}**
  {%- if param.annotation %} ({{ param.annotation }}){% endif %}
  {%- if param.default %} = ``{{ param.default }}``{% endif %}
  {%- if param.description %} -- {{ param.description }}{% endif %}
{%- endfor %}
{%- endif %}
{%- endmacro -%}

{%- macro render_attributes_section(obj) -%}
{%- if has_design %}
.. list-table::
   :header-rows: 1
   :widths: 25 25 50
   
   * - Attribute
     - Type
     - Description
   {%- for attr in obj.attributes|default([]) + obj.class_attributes|default([]) %}
   * - ``{{ attr.name }}``
     - {{ code.format_type(attr.annotation) if attr.annotation else 'Any' }}
     - {{ attr.short_description|default('—') }}
   {%- endfor %}
{%- else %}
{%- for attr in obj.attributes|default([]) + obj.class_attributes|default([]) %}
.. py:attribute:: {{ attr.name }}
   {%- if attr.annotation %}
   :type: {{ attr.annotation }}
   {%- endif %}
   {%- if attr.value %}
   :value: {{ attr.value }}
   {%- endif %}
   
   {%- if attr.docstring %}
   {{ attr.docstring|indent(3) }}
   {%- endif %}
{%- endfor %}
{%- endif %}
{%- endmacro -%}

{%- macro render_methods_tabbed(public, private, dunder) -%}
{%- set tabs = [] -%}
{%- if public %}{% set _ = tabs.append({'title': 'Public Methods (' ~ public|length ~ ')', 'content': render_method_list(public)}) %}{% endif -%}
{%- if private %}{% set _ = tabs.append({'title': 'Private Methods (' ~ private|length ~ ')', 'content': render_method_list(private)}) %}{% endif -%}
{%- if dunder %}{% set _ = tabs.append({'title': 'Special Methods (' ~ dunder|length ~ ')', 'content': render_method_list(dunder)}) %}{% endif -%}

{{ tabbed_content(tabs) }}
{%- endmacro -%}

{%- macro render_method_list(methods) -%}
{%- for method in methods|sort(attribute='name') %}
{%- if has_toggles %}
.. toggle::
   
   **{{ method.name }}**{{ method.signature|default('()') }}
   
   {%- if method.short_description %}
   {{ method.short_description }}
   {%- endif %}
{%- else %}
.. py:method:: {{ method.name }}{{ method.signature|default('()') }}
   
   {%- if method.docstring %}
   {{ method.docstring|indent(3) }}
   {%- endif %}
{%- endif %}
{%- endfor %}
{%- endmacro -%}

{%- macro render_inheritance_details(obj) -%}
{%- if has_design and has_mermaid %}
.. mermaid::
   
   graph TB
   {%- for base in obj.bases %}
   {{ base.name }} --> {{ obj.name }}
   {%- endfor %}
   {%- for sub in obj.subclasses|default([]) %}
   {{ obj.name }} --> {{ sub.name }}
   {%- endfor %}
   
   style {{ obj.name }} fill:#f9f,stroke:#333,stroke-width:4px
{%- endif %}

**Method Resolution Order (MRO):**

{%- if obj.mro %}
{%- for cls in obj.mro %}
{{ loop.index }}. `{{ cls }}`
{%- endfor %}
{%- endif %}
{%- endmacro -%}

{%- macro render_examples_tabbed(examples) -%}
{%- set tabs = [] -%}
{%- for example in examples %}
{%- set _ = tabs.append({'title': 'Example ' ~ loop.index, 'content': code.render_code_block(example, {'copybutton': true})}) -%}
{%- endfor %}
{{ tabbed_content(tabs) }}
{%- endmacro -%}