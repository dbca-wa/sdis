{% extends "mail_templated/base.tpl" %}

{% block subject %}
[SDIS] {{ object_name }} requires your attention
{% endblock %}

{% block html %}
Hi,

<p>{{ instigator.fullname }} has just run "{{ title }}" on
    <a href="{{ object_url }}">{{ object_name }}</a>.<br />
    This means: {{ explanation }}
</p>

<p>
    <a href="https://sdis.dpaw.wa.gov.au">SDIS</a> may require your input,
    review, or just wants to let you know that a document has been approved.
</p>

<p>
    Your action: Please visit <a href="{{ object_url }}">{{ object_name }}</a>
    and read, update, discuss with your team or supervisor, or comment as you
    see fit.
</p>

<p>
    When updating a document or project details, don't forget to exit the
    active text area and "save changes".
    When ready, you can take appropriate actions from the "Actions" menu -
    discuss with your team, the project leader, or your program leader if unclear.
</p>

<p>
    For your convenience, the link to
    <a href="{{ object_url }}">{{ object_name }}</a> is also listed under
    "My Tasks" on your <a href="https://sdis.dpaw.wa.gov.au">SDIS home page</a>.
</p>

<p>
    Cheers,<br />
    SDIS
</p>

<p>
ps. If you get stuck, please consult the
<a href="http://sdis.readthedocs.io/">SDIS Documentation</a>.
<br />
pps. If these messages clog your inbox, consider creating an
<a href="https://support.office.com/en-us/article/Manage-email-messages-by-using-rules-c24f5dea-9465-4df4-ad17-a50704d66c59">Outlook rule</a>.
</p>
{% endblock %}
