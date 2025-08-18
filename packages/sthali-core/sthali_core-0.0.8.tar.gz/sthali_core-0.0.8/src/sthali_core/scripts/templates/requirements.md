
---

### Requirements

#### Prerequisites
- `python {{ project["requires-python"] | safe }}`
- `pip` package manager

#### Runtime Dependencies
This project requires the following Python packages with specific versions:
{% for dependency in project["dependencies"] %}
- `{{ dependency | safe }}`
{% endfor %}

{% if project.get("optional-dependencies") %}
#### Optional Dependencies
This project has optional dependencies that can be installed for additional features:
{% for group, deps in project["optional-dependencies"].items() %}
##### {{ group }}
{% for dep in deps %}
- `{{ dep | safe }}`
{% endfor %}
{% endfor %}
{% endif %}
