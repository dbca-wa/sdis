{% extends "mail_templated/base.tpl" %}

{% block subject %}
[SDIS] {{ object_name }} requires your attention
{% endblock %}

{% block html %}
Hi,

<p>{{ instigator.fullname }} has just requested to run "{{ title }}" on
    <a href="{{ object_url }}">{{ object_name }}</a>.
    This action had the following effect: {{ explanation }}
</p>

<p>
    <a href="https://sdis.dpaw.wa.gov.au">SDIS</a> now requires your input!</a>
</p>

<p>
    Please update <a href="{{ object_url }}">{{ object_name }}</a>
    as you see fit, "save changes", then take any action from
    the "Actions" menu as appropriate.
</p>

<p>
    For your convenience, a link to <a href="{{ object_url }}">{{ object_name }}</a>
    is also listed under "My Tasks" on your
    <a href="https://sdis.dpaw.wa.gov.au">SDIS home page</a>.
</p>

Cheers,
SDIS

p.s. If you get stuck, please consult the
<a href="http://sdis.readthedocs.io/">SDIS Documentation</a>.
{% endblock %}
