{#- method.rst - Intelligent method template with extension integration -#}
{%- extends "python/_base/foundation.j2" -%}

{#- Import components -#}
{%- import "python/_components/code_blocks.j2" as code with context -%}

{%- block signature -%}
.. py:method:: {{ obj.name }}{{ obj.signature|default('()') }}
{%- if obj.is_async %}{{ '\n' }}   :async:{% endif %}
{%- if obj.is_classmethod %}{{ '\n' }}   :classmethod:{% endif %}
{%- if obj.is_staticmethod %}{{ '\n' }}   :staticmethod:{% endif %}
{%- if obj.is_property %}{{ '\n' }}   :property:{% endif %}
{%- if obj.is_abstractmethod %}{{ '\n' }}   :abstractmethod:{% endif %}

{%- if obj.docstring %}
   {{ obj.docstring|indent(3) }}
{%- endif %}
{%- endblock signature -%}

{%- block content -%}
{#- Method type badges -#}
{%- if has_design %}
{%- set badges = [] -%}
{%- if obj.is_async %}{% set _ = badges.append(badge('async', 'info')) %}{% endif -%}
{%- if obj.is_classmethod %}{% set _ = badges.append(badge('classmethod', 'primary')) %}{% endif -%}
{%- if obj.is_staticmethod %}{% set _ = badges.append(badge('staticmethod', 'secondary')) %}{% endif -%}
{%- if obj.is_property %}{% set _ = badges.append(badge('property', 'success')) %}{% endif -%}
{%- if obj.is_abstractmethod %}{% set _ = badges.append(badge('abstract', 'warning')) %}{% endif -%}
{%- if obj.is_generator %}{% set _ = badges.append(badge('generator', 'info')) %}{% endif -%}

{%- if badges %}
{{ badges|join(' ') }}
{%- endif %}
{%- endif %}

{#- Decorators -#}
{%- if obj.decorators %}

Decorators
----------

{%- for decorator in obj.decorators %}
* ``@{{ decorator }}``
{%- endfor %}
{%- endif %}

{#- Parameters for methods with many params -#}
{%- if obj.parameters and obj.parameters|length > 2 %}

Parameters
----------

{%- if has_design %}
.. list-table::
   :header-rows: 1
   :widths: 20 25 15 40
   
   * - Parameter
     - Type
     - Default
     - Description
   {%- for param in obj.parameters if param.name != 'self' %}
   * - ``{{ param.name }}``
     - {{ code.format_type(param.annotation) if param.annotation else 'Any' }}
     - {{ '``' ~ param.default ~ '``' if param.default else '*required*' }}
     - {{ param.description|default('—') }}
   {%- endfor %}
{%- else %}
{%- for param in obj.parameters if param.name != 'self' %}
**{{ param.name }}**
    {%- if param.annotation %} ({{ param.annotation }}){% endif %}
    {%- if param.default %} = ``{{ param.default }}``{% endif %}
    {%- if param.description %} -- {{ param.description }}{% endif %}
{%- endfor %}
{%- endif %}
{%- endif %}

{#- Return value -#}
{%- if obj.returns %}

Returns
-------

{%- if obj.returns %}
:rtype: {{ obj.returns }}
{%- endif %}

{%- if obj.return_description %}
{{ obj.return_description }}
{%- endif %}
{%- endif %}

{#- Property getter/setter info -#}
{%- if obj.is_property %}
{%- if obj.setter %}

.. note::
   
   This property has both getter and setter methods.
{%- else %}

.. note::
   
   This is a read-only property.
{%- endif %}
{%- endif %}

{#- Raises/Exceptions -#}
{%- if obj.raises %}

Raises
------

{%- for exception in obj.raises %}
**{{ exception.type }}**
    {{ exception.description }}
{%- endfor %}
{%- endif %}

{#- Method examples -#}
{%- if obj.examples %}

Examples
--------

{%- if has_tabs and obj.examples|length > 1 %}
{{ tabbed_content([
    {'title': 'Example ' ~ loop.index, 'content': code.render_code_block(example)}
    for example in obj.examples
]) }}
{%- else %}
{%- for example in obj.examples %}
{{ code.render_code_block(example) }}
{%- endfor %}
{%- endif %}
{%- endif %}

{#- Overrides information -#}
{%- if obj.overrides %}

.. admonition:: Overrides
   :class: note

   This method overrides :meth:`{{ obj.overrides }}`.
{%- endif %}

{#- Implementation notes -#}
{%- if obj.implementation_notes %}

Implementation Notes
--------------------

{{ obj.implementation_notes }}
{%- endif %}
{%- endblock content -%}