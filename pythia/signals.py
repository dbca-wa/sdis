from __future__ import unicode_literals

from django_browserid.signals import user_created


def persona_user_created(sender, user, **kwargs):
    """
    When a user logs in via Persona, a new user is created. Ensure that the
    user instance is restricted until a member of staff activates the account.

    A persona user is not a staff member by default and has no groups.
    """
    user.is_external = True
    user.is_staff = False
    user.save()

    map(lambda x: user.groups.remove(x), user.groups.all())


user_created.connect(persona_user_created)
