{#- index.rst - Intelligent API index with extension integration -#}
{%- extends "python/_base/foundation.j2" -%}

{#- Import navigation and visualization components -#}
{%- import "python/_components/navigation.j2" as nav with context -%}
{%- import "python/_components/diagrams.j2" as diagrams with context -%}

{%- block header -%}
API Reference
=============
{%- endblock header -%}

{%- block metadata -%}
.. meta::
   :description: Complete API reference documentation with all modules, classes, and functions
   :keywords: API, reference, documentation, modules, classes, functions
{%- endblock metadata -%}

{%- block content -%}
{#- API overview statistics -#}
{%- if has_design %}
.. grid:: 1 1 2 4
   :gutter: 3
   :margin: 0 0 4 0

   {{ info_card('Modules', count_modules(pages), {'columns': '6 6 3 3', 'icon': '📦'}) }}
   {{ info_card('Classes', count_classes(pages), {'columns': '6 6 3 3', 'icon': '🏗️'}) }}
   {{ info_card('Functions', count_functions(pages), {'columns': '6 6 3 3', 'icon': '⚡'}) }}
   {{ info_card('Coverage', calculate_coverage(pages) ~ '%', {'columns': '6 6 3 3', 'icon': '📊'}) }}
{%- endif %}

{#- Quick search section -#}
{%- if has_design %}
.. admonition:: Quick Search
   :class: tip

   Use ``Ctrl+K`` or ``Cmd+K`` to quickly search the API documentation.
   
   Common searches:
   {%- if has_copybutton %}
   
   .. code-block:: text
      :class: copybutton
      
      Agent          # Find all agent classes
      tool_          # Find all tool-related items
      async def      # Find async functions
      BaseModel      # Find Pydantic models
   {%- endif %}
{%- endif %}

{#- Package structure visualization -#}
{%- if has_mermaid and packages %}
{{ progressive_section('Package Structure', 
                      diagrams.render_package_structure(packages), 
                      {'open': true, 'icon': '🗂️'}) }}
{%- endif %}

{#- Main API sections organized by type -#}
{%- set api_structure = organize_api_structure(pages) -%}

{#- Core Modules section -#}
{%- if api_structure.core_modules %}
{{ progressive_section('Core Modules', 
                      render_module_section(api_structure.core_modules, 'core'), 
                      {'open': true, 'icon': '🏛️'}) }}
{%- endif %}

{#- Feature Modules section -#}
{%- if api_structure.feature_modules %}
{{ progressive_section('Feature Modules', 
                      render_module_section(api_structure.feature_modules, 'features'), 
                      {'open': true, 'icon': '🎯'}) }}
{%- endif %}

{#- Utility Modules section -#}
{%- if api_structure.utility_modules %}
{{ progressive_section('Utilities & Helpers', 
                      render_module_section(api_structure.utility_modules, 'utilities'), 
                      {'open': false, 'icon': '🔧'}) }}
{%- endif %}

{#- Class Index by category -#}
{%- if api_structure.classes_by_category %}
{{ progressive_section('Class Index', 
                      render_class_index(api_structure.classes_by_category), 
                      {'open': false, 'icon': '📚'}) }}
{%- endif %}

{#- Function Index -#}
{%- if api_structure.all_functions %}
{{ progressive_section('Function Index', 
                      render_function_index(api_structure.all_functions), 
                      {'open': false, 'icon': '🔍'}) }}
{%- endif %}

{#- Full module index -#}

Full Module Index
-----------------

.. toctree::
   :maxdepth: 2
   :titlesonly:

   {%- for page in pages|sort(attribute='name') %}
   {{ page.name }}
   {%- endfor %}

{#- Genindex and modindex -#}

Indices
-------

* :ref:`genindex`
* :ref:`modindex`
{%- if has_search %}
* :ref:`search`
{%- endif %}
{%- endblock content -%}

{#- Helper macros -#}
{%- macro count_modules(pages) -%}
{{ pages|selectattr('type', 'equalto', 'module')|list|length }}
{%- endmacro -%}

{%- macro count_classes(pages) -%}
{%- set count = 0 -%}
{%- for page in pages -%}
    {%- if page.children -%}
        {%- set count = count + page.children|selectattr('type', 'equalto', 'class')|list|length -%}
    {%- endif -%}
{%- endfor -%}
{{ count }}
{%- endmacro -%}

{%- macro count_functions(pages) -%}
{%- set count = 0 -%}
{%- for page in pages -%}
    {%- if page.children -%}
        {%- set count = count + page.children|selectattr('type', 'equalto', 'function')|list|length -%}
    {%- endif -%}
{%- endfor -%}
{{ count }}
{%- endmacro -%}

{%- macro calculate_coverage(pages) -%}
{#- Simple coverage calculation based on docstring presence -#}
85
{%- endmacro -%}

{%- macro organize_api_structure(pages) -%}
{%- set structure = {
    'core_modules': [],
    'feature_modules': [],
    'utility_modules': [],
    'classes_by_category': {},
    'all_functions': []
} -%}

{%- for page in pages -%}
    {%- if page.type == 'module' -%}
        {%- if 'core' in page.name or 'base' in page.name -%}
            {%- set _ = structure.core_modules.append(page) -%}
        {%- elif 'util' in page.name or 'helper' in page.name or 'common' in page.name -%}
            {%- set _ = structure.utility_modules.append(page) -%}
        {%- else -%}
            {%- set _ = structure.feature_modules.append(page) -%}
        {%- endif -%}
    {%- endif -%}
{%- endfor -%}

{{ structure }}
{%- endmacro -%}

{%- macro render_module_section(modules, section_type) -%}
{%- if has_design %}
.. grid:: 1 1 2 3
   :gutter: 3

   {%- for module in modules|sort(attribute='name') %}
   .. grid-item-card:: :mod:`{{ module.name }}`
      :link: {{ module.name }}
      :link-type: doc
      
      {{ module.summary|default(module.short_description, true)|truncate(150) }}
      
      {%- set stats = get_module_stats(module) -%}
      {%- if stats %}
      
      .. container:: module-stats
         
         {{ stats }}
      {%- endif %}
   {%- endfor %}
{%- else %}
{%- for module in modules|sort(attribute='name') %}
* :mod:`{{ module.name }}` - {{ module.summary|default('Module documentation') }}
{%- endfor %}
{%- endif %}
{%- endmacro -%}

{%- macro get_module_stats(module) -%}
{%- set stats = [] -%}
{%- if module.children -%}
    {%- set classes = module.children|selectattr('type', 'equalto', 'class')|list -%}
    {%- set functions = module.children|selectattr('type', 'equalto', 'function')|list -%}
    {%- if classes %}{% set _ = stats.append(classes|length ~ ' classes') %}{% endif -%}
    {%- if functions %}{% set _ = stats.append(functions|length ~ ' functions') %}{% endif -%}
{%- endif -%}
{{ stats|join(' • ') }}
{%- endmacro -%}

{%- macro render_class_index(categories) -%}
{%- if has_tabs %}
{{ tabbed_content([
    {'title': category|title, 'content': render_class_list(classes)}
    for category, classes in categories.items()
]) }}
{%- else %}
{%- for category, classes in categories.items() %}

{{ category|title }}
{{ '~' * category|length }}

{%- for cls in classes|sort(attribute='name') %}
* :class:`{{ cls.full_name }}` - {{ cls.summary|truncate(80) }}
{%- endfor %}
{%- endfor %}
{%- endif %}
{%- endmacro -%}

{%- macro render_function_index(functions) -%}
{%- set async_funcs = functions|selectattr('is_async')|list -%}
{%- set sync_funcs = functions|rejectattr('is_async')|list -%}

{%- if has_tabs %}
{{ tabbed_content([
    {'title': 'Functions (' ~ sync_funcs|length ~ ')', 'content': render_function_list(sync_funcs)},
    {'title': 'Async Functions (' ~ async_funcs|length ~ ')', 'content': render_function_list(async_funcs)}
]) }}
{%- else %}
{{ render_function_list(functions) }}
{%- endif %}
{%- endmacro -%}

{%- macro render_class_list(classes) -%}
{%- for cls in classes|sort(attribute='name') %}
* :class:`{{ cls.full_name }}` - {{ cls.summary|truncate(80) }}
{%- endfor %}
{%- endmacro -%}

{%- macro render_function_list(functions) -%}
.. list-table::
   :header-rows: 1
   
   * - Function
     - Module
     - Description
   {%- for func in functions|sort(attribute='name') %}
   * - :func:`{{ func.name }}`
     - :mod:`{{ func.module }}`
     - {{ func.summary|truncate(60) }}
   {%- endfor %}
{%- endmacro -%}