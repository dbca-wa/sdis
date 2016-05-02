"""Custom backends providing permission checks, authentication
"""

from django.contrib.auth import get_user_model
from django_auth_ldap.backend import LDAPBackend
from guardian.backends import ObjectPermissionBackend


def get_doc_users(obj):
    """For a given object of any documents model, return project team members.
    """
    if obj is not None:
        User = get_user_model()
        pks = obj.project.pythia_membership_project.values_list(
            'user', flat=True)
        return set(User.objects.filter(pk__in=pks))
    else:
        return set()


def get_doc_admins(obj):
    """For a given object of any documents model, return core project members.

    Includes project_owner, data_custodian and site_custodian.
    Excludes other team members.
    """
    return (obj is not None and set((obj.project.project_owner,
                                     obj.project.data_custodian,
                                     obj.project.site_custodian)) or
            set())


def get_doc_reviewers(obj):
    return (obj is not None and set((obj.project.program.program_leader,)) or
            set())


def get_doc_editors(obj):
    # TODO: who is ARAR editors???
    return (obj is not None and set() or set())


PERMISSIONS = {
    'team': lambda u, o: u in get_doc_users(o),
    'can_submit': lambda u, o: u in get_doc_admins(o),
    'can_review': lambda u, o: u in get_doc_reviewers(o),
    'can_approve': lambda u, o: u in get_doc_editors(o),
    }


class PythiaBackend(object):
    def authenticate(self, **kwargs):
        return None

    def get_group_permissions(self, user_obj, obj=None):
        return set()

    def get_all_permissions(self, user_obj, obj=None):
        return set()

    def has_perm(self, user_obj, perm, obj=None):
        # deals with 'documents.can_submit', 'documents.can_review',
        # 'documents.can_approve'
        if not user_obj.is_active:
            return False
        if user_obj.is_superuser:
            return True
        module, perm = perm.split('.', 2)

        if module == "documents":
            return PERMISSIONS.get(perm, lambda _, __: False)(user_obj, obj)

        return False

    def has_module_perms(self, user_obj, app_label):
        return False

    def get_user(self, user_id):
        return None


class EmailBackend(ObjectPermissionBackend):
    """
    An authentication backend to handle user requirements in DPaW.

    It will authenticate a user against LDAP if it can't find a user entry in
    the database, and will allow users to login with their DPaW emails.

    It also handles object permissions through guardian's object permission
    framework.
    """
    def authenticate(self, username=None, password=None):
        """
        Attempt to authenticate a particular user. The username field is taken
        to be an email address and checked against LDAP if the user cannot
        be found.

        Always returns an instance of `django.contrib.auth.models.User` on
        success, otherwise returns None.
        """
        User = get_user_model()
        if password is None:
            return None
        try:
            user = User.objects.get(email__iexact=username)
            if user.check_password(password):
                return user
            else:
                try:
                    ldapauth = LDAPBackend()
                    return ldapauth.authenticate(username=user.username,
                                                 password=password)
                except:
                    return None
        except User.DoesNotExist:
            try:
                ldapauth = LDAPBackend()
                user = ldapauth.authenticate(
                    username=username, password=password)
                if user is None:
                    return None

                first_name = user.first_name
                last_name = user.last_name
                email = user.email
                if email:
                    if User.objects.filter(email__iexact=email).count() > 1:
                        user.delete()
                    user = User.objects.get(email__iexact=email)
                    user.first_name, user.last_name = first_name, last_name
                    user.save()
                else:
                    user = User.objects.get(username=username)
                    user.first_name, user.last_name = first_name, last_name
                    user.save()
                return user
            except Exception, e:
                print e
                return None

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
