{% extends "mail_templated/base.tpl" %}

{% block subject %}
[SDIS] {{ object_name }} requires your attention
{% endblock %}

{% block html %}
Hi {{ user.first_name }},

<p>{{ instigator }} has just requested to {{ title }} the
<a href="{{ object_url }}">{{ object_name }}</a>.
This action had the following effect: {{ explanation }}</p>

<p><a href="https://sdis.dpaw.wa.gov.au">SDIS</a> now requires your input!</a>

<p>If required, please update <a href="{{ object_url }}">{{ object_name }}</a>
    as you see fit (don't forget to "save changes"), then take any action from
    the "Actions" menu as appropriate.</p>

<p>For your convenience, a link to <a href="{{ object_url }}">{{ object_name }}</a>
    is also listed under "My Tasks" on your
    <a href="https://sdis.dpaw.wa.gov.au">SDIS home page</a>.</p>

Cheers,
SDIS

p.s. If you get stuck, please consult the
<a href="http://sdis.readthedocs.io/">SDIS Documentation</a>.
{% endblock %}
