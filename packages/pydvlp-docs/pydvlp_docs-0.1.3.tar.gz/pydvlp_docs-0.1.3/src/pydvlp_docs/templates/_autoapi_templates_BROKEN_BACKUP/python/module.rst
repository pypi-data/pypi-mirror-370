{#- module.rst - Intelligent module template with extension integration -#}
{%- extends "python/_base/progressive.j2" -%}

{#- Import navigation components -#}
{%- import "python/_components/navigation.j2" as nav with context -%}
{%- import "python/_components/diagrams.j2" as diagrams with context -%}

{%- block header -%}
{%- if obj.all %}
:mod:`{{ obj.name }}`
{{ "=" * (obj.name|length + 8) }}
{%- else %}
{{ obj.name }}
{{ "=" * obj.name|length }}
{%- endif %}
{%- endblock header -%}

{%- block signature -%}
.. py:module:: {{ obj.name }}
{%- if obj.summary %}

   {{ obj.summary|indent(3) }}
{%- endif %}
{%- endblock signature -%}

{%- block content -%}
{#- Module overview with cards -#}
{%- if has_design %}
{{ nav.render_module_overview_cards(obj) }}
{%- endif %}

{#- Module-level attributes -#}
{%- if obj.attributes %}

Module Attributes
-----------------

{%- for attr in obj.attributes %}
.. py:data:: {{ attr.name }}
   {%- if attr.annotation %}
   :type: {{ attr.annotation }}
   {%- endif %}
   {%- if attr.value %}
   :value: {{ attr.value|truncate(50) }}
   {%- endif %}
   
   {%- if attr.docstring %}
   {{ attr.docstring|indent(3) }}
   {%- endif %}
{%- endfor %}
{%- endif %}

{#- Submodules and subpackages -#}
{%- set has_submodules = obj.submodules or obj.subpackages -%}
{%- if has_submodules %}

{{ progressive_section('Submodules', render_submodules_section(obj), {'open': true, 'icon': '📦'}) }}
{%- endif %}

{#- Module contents organized by type -#}
{%- set contents = organize_module_contents(obj) -%}

{#- Classes section -#}
{%- if contents.classes %}
{{ progressive_section('Classes (' ~ contents.classes|length ~ ')', 
                      render_classes_section(contents.classes), 
                      {'open': true, 'icon': '🏗️'}) }}
{%- endif %}

{#- Functions section -#}
{%- if contents.functions %}
{{ progressive_section('Functions (' ~ contents.functions|length ~ ')', 
                      render_functions_section(contents.functions), 
                      {'open': true, 'icon': '⚡'}) }}
{%- endif %}

{#- Exceptions section -#}
{%- if contents.exceptions %}
{{ progressive_section('Exceptions (' ~ contents.exceptions|length ~ ')', 
                      render_exceptions_section(contents.exceptions), 
                      {'open': false, 'icon': '⚠️'}) }}
{%- endif %}

{#- Type aliases and constants -#}
{%- if contents.type_aliases or contents.constants %}
{{ progressive_section('Types & Constants', 
                      render_types_constants_section(contents), 
                      {'open': false, 'icon': '🔤'}) }}
{%- endif %}

{#- Module dependency graph -#}
{%- if has_mermaid and (obj.imports or obj.imported_by) %}
{{ progressive_section('Module Dependencies', 
                      diagrams.render_dependency_graph(obj), 
                      {'open': false, 'icon': '🔗'}) }}
{%- endif %}

{#- Module source metrics -#}
{%- if obj.source_metrics %}
{{ progressive_section('Source Metrics', 
                      render_source_metrics(obj.source_metrics), 
                      {'open': false, 'icon': '📊'}) }}
{%- endif %}
{%- endblock content -%}

{#- Helper macros -#}
{%- macro organize_module_contents(obj) -%}
{%- set contents = {
    'classes': [],
    'functions': [],
    'exceptions': [],
    'type_aliases': [],
    'constants': []
} -%}

{%- for child in obj.children|default([]) -%}
    {%- if child.type == 'class' -%}
        {%- if 'Exception' in child.bases|map(attribute='name')|list or 'Error' in child.bases|map(attribute='name')|list -%}
            {%- set _ = contents.exceptions.append(child) -%}
        {%- else -%}
            {%- set _ = contents.classes.append(child) -%}
        {%- endif -%}
    {%- elif child.type == 'function' -%}
        {%- set _ = contents.functions.append(child) -%}
    {%- elif child.type == 'data' -%}
        {%- if child.name.isupper() -%}
            {%- set _ = contents.constants.append(child) -%}
        {%- else -%}
            {%- set _ = contents.type_aliases.append(child) -%}
        {%- endif -%}
    {%- endif -%}
{%- endfor -%}

{{ contents }}
{%- endmacro -%}

{%- macro render_submodules_section(obj) -%}
{%- if obj.subpackages %}
**Subpackages:**

.. toctree::
   :maxdepth: 1
   
{%- for subpkg in obj.subpackages|sort(attribute='name') %}
   {{ subpkg.name }}/index
{%- endfor %}
{%- endif %}

{%- if obj.submodules %}
**Submodules:**

.. toctree::
   :maxdepth: 1
   
{%- for submod in obj.submodules|sort(attribute='name') %}
   {{ submod.name }}
{%- endfor %}
{%- endif %}
{%- endmacro -%}

{%- macro render_classes_section(classes) -%}
{%- if has_design %}
.. grid:: 1 1 2 2
   :gutter: 3

   {%- for cls in classes|sort(attribute='name') %}
   .. grid-item-card:: :class:`{{ cls.name }}`
      :link: {{ cls.name|lower }}
      :link-type: ref
      
      {%- if cls.summary %}
      {{ cls.summary|truncate(150) }}
      {%- endif %}
      
      {%- set stats = [] -%}
      {%- if cls.methods %}{% set _ = stats.append(cls.methods|length ~ ' methods') %}{% endif -%}
      {%- if cls.attributes %}{% set _ = stats.append(cls.attributes|length ~ ' attrs') %}{% endif -%}
      {%- if stats %}
      
      *{{ stats|join(', ') }}*
      {%- endif %}
   {%- endfor %}
{%- else %}
.. autosummary::
   :toctree:
   :template: custom-class-template.rst

   {%- for cls in classes|sort(attribute='name') %}
   {{ obj.name }}.{{ cls.name }}
   {%- endfor %}
{%- endif %}
{%- endmacro -%}

{%- macro render_functions_section(functions) -%}
{%- set groups = functions|groupby('is_async') -%}

{%- for is_async, funcs in groups %}
{%- if is_async %}
**Async Functions:**
{%- else %}
**Functions:**
{%- endif %}

{%- if has_design %}
.. list-table::
   :header-rows: 1
   :widths: 30 70
   
   * - Function
     - Description
   {%- for func in funcs|sort(attribute='name') %}
   * - :func:`{{ func.name }}`
     - {{ func.summary|default(func.short_description, true)|default('—') }}
   {%- endfor %}
{%- else %}
{%- for func in funcs|sort(attribute='name') %}
.. autofunction:: {{ obj.name }}.{{ func.name }}
   :noindex:
{%- endfor %}
{%- endif %}
{%- endfor %}
{%- endmacro -%}

{%- macro render_exceptions_section(exceptions) -%}
{%- if has_design %}
.. admonition:: Exception Hierarchy
   :class: error

   {%- if has_mermaid %}
   .. mermaid::
      
      graph LR
      {%- for exc in exceptions %}
      {%- if exc.bases %}
      {%- for base in exc.bases %}
      {{ base.name }} --> {{ exc.name }}
      {%- endfor %}
      {%- else %}
      Exception --> {{ exc.name }}
      {%- endif %}
      {%- endfor %}
   {%- endif %}
{%- endif %}

{%- for exc in exceptions|sort(attribute='name') %}
.. autoexception:: {{ obj.name }}.{{ exc.name }}
   :noindex:
   :members:
{%- endfor %}
{%- endmacro -%}

{%- macro render_types_constants_section(contents) -%}
{%- if contents.type_aliases %}
**Type Aliases:**

{%- for alias in contents.type_aliases|sort(attribute='name') %}
.. py:data:: {{ alias.name }}
   {%- if alias.annotation %}
   :type: {{ alias.annotation }}
   {%- endif %}
   
   {%- if alias.docstring %}
   {{ alias.docstring|indent(3) }}
   {%- endif %}
{%- endfor %}
{%- endif %}

{%- if contents.constants %}
**Constants:**

.. list-table::
   :header-rows: 1
   
   * - Constant
     - Value
     - Description
   {%- for const in contents.constants|sort(attribute='name') %}
   * - ``{{ const.name }}``
     - ``{{ const.value|truncate(30) }}``
     - {{ const.short_description|default('—') }}
   {%- endfor %}
{%- endif %}
{%- endmacro -%}

{%- macro render_source_metrics(metrics) -%}
.. list-table::
   :header-rows: 1
   
   * - Metric
     - Value
   * - Lines of Code
     - {{ metrics.loc|default(0) }}
   * - Docstring Coverage
     - {{ metrics.docstring_coverage|default(0) }}%
   * - Type Hint Coverage
     - {{ metrics.type_hint_coverage|default(0) }}%
   * - Cyclomatic Complexity
     - {{ metrics.complexity|default('N/A') }}
{%- endmacro -%}