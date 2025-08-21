{#- function.rst - Intelligent function template with extension integration -#}
{%- extends "python/_base/foundation.j2" -%}

{#- Import code components -#}
{%- import "python/_components/code_blocks.j2" as code with context -%}
{%- import "python/_components/interactive.j2" as interactive with context -%}

{%- block signature -%}
.. py:function:: {{ obj.name }}{{ obj.signature|default('()') }}
{%- if obj.is_async %}{{ '\n' }}   :async:{% endif %}
{%- if obj.module %}{{ '\n' }}   :module: {{ obj.module }}{% endif %}

{%- if obj.docstring %}
   {{ obj.docstring|indent(3) }}
{%- endif %}
{%- endblock signature -%}

{%- block content -%}
{#- Function overview card -#}
{%- if has_design and (obj.parameters or obj.returns or obj.raises) %}
.. grid:: 1 1 2 2
   :gutter: 2
   :margin: 0 0 3 0

   {%- if obj.parameters %}
   {{ info_card('Parameters', render_parameters_card(obj.parameters), {'columns': '12 12 6 6', 'color': 'info'}) }}
   {%- endif %}
   
   {%- if obj.returns or obj.yields %}
   {{ info_card('Returns', render_returns_card(obj), {'columns': '12 12 6 6', 'color': 'success'}) }}
   {%- endif %}
{%- endif %}

{#- Detailed parameter documentation -#}
{%- if obj.parameters and obj.parameters|length > 3 %}
{{ progressive_section('Parameters (' ~ obj.parameters|length ~ ')', 
                      render_detailed_parameters(obj.parameters), 
                      {'open': true, 'icon': '📥'}) }}
{%- elif obj.parameters %}

Parameters
----------

{{ render_detailed_parameters(obj.parameters) }}
{%- endif %}

{#- Return value documentation -#}
{%- if obj.returns and obj.return_description %}

Returns
-------

{%- if obj.returns %}
**Type:** {{ code.format_type(obj.returns) }}
{%- endif %}

{%- if obj.return_description %}
{{ obj.return_description }}
{%- endif %}
{%- endif %}

{#- Yields documentation for generators -#}
{%- if obj.yields %}

Yields
------

{%- if obj.yields %}
**Type:** {{ code.format_type(obj.yields) }}
{%- endif %}

{%- if obj.yield_description %}
{{ obj.yield_description }}
{%- endif %}
{%- endif %}

{#- Exceptions/Raises -#}
{%- if obj.raises %}

Raises
------

{%- for exception in obj.raises %}
{%- if has_design %}
.. admonition:: {{ exception.type }}
   :class: error

   {{ exception.description }}
{%- else %}
**{{ exception.type }}**
    {{ exception.description }}
{%- endif %}
{%- endfor %}
{%- endif %}

{#- Type hints visualization -#}
{%- if has_mermaid and obj.parameters and (obj.returns or obj.yields) %}
{{ progressive_section('Type Flow', 
                      render_type_flow_diagram(obj), 
                      {'open': false, 'icon': '🔄'}) }}
{%- endif %}

{#- Interactive examples -#}
{%- if obj.examples and has_exec %}
{{ progressive_section('Interactive Examples', 
                      interactive.render_executable_examples(obj.examples), 
                      {'open': true, 'icon': '🚀'}) }}
{%- endif %}

{#- Usage patterns -#}
{%- if obj.usage_patterns %}
{{ progressive_section('Common Usage Patterns', 
                      render_usage_patterns(obj.usage_patterns), 
                      {'open': false, 'icon': '💡'}) }}
{%- endif %}

{#- Performance notes -#}
{%- if obj.performance_notes %}
{{ progressive_section('Performance Considerations', 
                      render_performance_notes(obj.performance_notes), 
                      {'open': false, 'icon': '⚡'}) }}
{%- endif %}

{#- Related functions -#}
{%- if obj.related_functions %}

See Also
--------

{%- for func in obj.related_functions %}
* :func:`{{ func }}` -- {{ get_function_summary(func) }}
{%- endfor %}
{%- endif %}
{%- endblock content -%}

{#- Helper macros -#}
{%- macro render_parameters_card(params) -%}
{%- for param in params[:3] %}
• **{{ param.name }}**
  {%- if param.annotation %} ({{ param.annotation|truncate(20) }}){% endif %}
  {%- if param.default %} = ``{{ param.default|truncate(15) }}``{% endif %}
{%- endfor %}
{%- if params|length > 3 %}

*... and {{ params|length - 3 }} more*
{%- endif %}
{%- endmacro -%}

{%- macro render_returns_card(obj) -%}
{%- if obj.returns %}
**Type:** ``{{ obj.returns|truncate(50) }}``
{%- elif obj.yields %}
**Yields:** ``{{ obj.yields|truncate(50) }}``
{%- endif %}

{%- if obj.return_description %}
{{ obj.return_description|truncate(100) }}
{%- endif %}
{%- endmacro -%}

{%- macro render_detailed_parameters(params) -%}
{%- if has_design %}
.. list-table::
   :header-rows: 1
   :widths: 20 20 15 45
   
   * - Parameter
     - Type
     - Default
     - Description
   {%- for param in params %}
   * - ``{{ param.name }}``
     - {{ code.format_type(param.annotation) if param.annotation else 'Any' }}
     - {{ '``' ~ param.default ~ '``' if param.default else '*required*' }}
     - {{ param.description|default('—') }}
   {%- endfor %}
{%- else %}
{%- for param in params %}
**{{ param.name }}**
    {%- if param.annotation %}
    Type: {{ param.annotation }}
    {%- endif %}
    {%- if param.default %}
    Default: ``{{ param.default }}``
    {%- endif %}
    {%- if param.description %}
    
    {{ param.description|indent(4) }}
    {%- endif %}
{%- endfor %}
{%- endif %}
{%- endmacro -%}

{%- macro render_type_flow_diagram(obj) -%}
.. mermaid::
   :align: center
   
   graph LR
   {%- for param in obj.parameters %}
   {{ param.name }}[{{ param.name }}: {{ param.annotation|default('Any') }}] --> F
   {%- endfor %}
   F[{{ obj.name }}]
   {%- if obj.returns %}
   F --> R[Returns: {{ obj.returns }}]
   {%- elif obj.yields %}
   F --> Y[Yields: {{ obj.yields }}]
   {%- endif %}
   
   style F fill:#f9f,stroke:#333,stroke-width:2px
{%- endmacro -%}

{%- macro render_usage_patterns(patterns) -%}
{%- if has_tabs %}
{{ tabbed_content([
    {'title': pattern.name, 'content': code.render_code_block(pattern.code)}
    for pattern in patterns
]) }}
{%- else %}
{%- for pattern in patterns %}
**{{ pattern.name }}:**

{{ code.render_code_block(pattern.code) }}
{%- endfor %}
{%- endif %}
{%- endmacro -%}

{%- macro render_performance_notes(notes) -%}
{%- if has_design %}
.. admonition:: Performance Notes
   :class: tip

   {{ notes }}
{%- else %}
{{ notes }}
{%- endif %}
{%- endmacro -%}

{%- macro get_function_summary(func_name) -%}
{#- This would look up the function summary from the documentation data -#}
Related function
{%- endmacro -%}