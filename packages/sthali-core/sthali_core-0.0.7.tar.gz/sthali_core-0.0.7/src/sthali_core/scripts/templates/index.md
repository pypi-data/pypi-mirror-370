<p align="center">
    <a href="https://{{ organization_name }}.github.io/{{ project['name'] }}/images/{{ project['name'] }}.svg">
        <img src="https://{{ organization_name }}.github.io/{{ project['name'] }}/images/{{ project['name'] }}.svg" alt="{{ project['name'] }}">
    </a>
    <em>{{ project["description"] | safe }}</em>
</p>
<p align="center">
    <a href="https://github.com/{{ organization_name }}/{{ project['name'] }}/actions/workflows/tests.yml" target="_blank">
        <img src="https://github.com/{{ organization_name }}/{{ project['name'] }}/actions/workflows/tests.yml/badge.svg" alt="">
    </a>
    <a href="https://github.com/{{ organization_name }}/{{ project['name'] }}/actions/workflows/deploy.yml" target="_blank">
        <img src="https://github.com/{{ organization_name }}/{{ project['name'] }}/actions/workflows/deploy.yml/badge.svg" alt="">
    </a>
    <a href="https://github.com/{{ organization_name }}/{{ project['name'] }}/actions/workflows/docs.yml" target="_blank">
        <img src="https://github.com/{{ organization_name }}/{{ project['name'] }}/actions/workflows/docs.yml/badge.svg?branch=development" alt="">
    </a>
</p>

<p align="center">
    <a href="https://{{ organization_name }}.github.io/{{ project['name'] }}/license/" target="_blank">
        <img alt="License" src="https://img.shields.io/github/license/{{ organization_name }}/{{ project['name'] }}">
    </a>
    <a href="https://github.com/{{ organization_name }}/{{ project['name'] }}/releases" target="_blank">
        <img alt="Release" src="https://img.shields.io/github/v/release/{{ organization_name }}/{{ project['name'] }}">
    </a>
</p>

**Docs**: [https://{{ organization_name }}.github.io/{{ project["name"] }}/](https://{{ organization_name }}.github.io/{{ project["name"] }}/)

**PyPI**: [https://pypi.org/project/{{ project["name"] }}/](https://pypi.org/project/{{ project["name"] }}/)

**Source**: [https://github.com/{{ organization_name }}/{{ project["name"] }}/](https://github.com/{{ organization_name }}/{{ project["name"] }}/)

**Board**: [https://github.com/users/{{ organization_name }}/projects/1/](https://github.com/users/{{ organization_name }}/projects/1/)
