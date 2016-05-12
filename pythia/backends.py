"""Custom Pythia backends providing authentication.

PythiaBackend providing custom permission checks has been retired in favour
of Project and Document transition permission checks against Project and
Document model methods providing the correct audience for each transition.

# PythiaBackend provides a custom `has_perm`, which via
# `pythia.backends.{DOC|PROJECT}_PERMISSONS`, dicts of permission names
# (submit, review, approve) and lambda functions, looks up the correct audience
# for these permissions.
#
# The functions `get_{team|admins}`, and the constants SMT and SCD
# encapsulate the business logic of Document and Project audiences.
"""

from django.contrib.auth import get_user_model
from django_auth_ldap.backend import LDAPBackend
from guardian.backends import ObjectPermissionBackend

# from django.contrib.auth.models import Group
# def get_team(obj):
#     """Return project team members for any projects or documents model.
#
#     Team members are the widest audience who should be able to submit.
#     Non-team members have to reason to submit a Document.
#     """
#     # User = get_user_model()
#     if obj is not None:
#         if obj.opts.app_label == 'projects':
#             p = obj
#         elif obj.opts.app_label == 'documents':
#             p = obj.project
#         else:
#             return set()
#         team = [m.user for m in p.projectmembership_set.all()]
#         # pks = p.projectmembership_set.values_list('user', flat=True)
#         # team = set(User.objects.filter(pk__in=pks))
#         print("get_team for {0} is {1}".format(obj.__str__(), team))
#         return team
#     else:
#         return set()
#
#
# def get_admins(obj):
#     """For a given object of any documents model, return core project members.
#
#     Includes project_owner, data_custodian and site_custodian.
#     Excludes other team members.
#
#     Doc admins are the minimum audience to "submit" Documents.
#     At the least, they should be able to "submit" Documents.
#
#     Returns an empty set if the object does not exist, or is not a project or
#     document model.
#     """
#     if obj is not None:
#         if obj.opts.app_label == 'projects':
#             p = obj
#         elif obj.opts.app_label == 'documents':
#             p = obj.project
#         else:
#             return set()
#         return set(p.project_owner, p.data_custodian, p.site_custodian)
#     else:
#         return set()
#
# smt, created = Group.objects.get_or_create(name='SMT')
# scd, created = Group.objects.get_or_create(name='SCD')
#
# SMT = smt.user_set.all()
# SCD = scd.user_set.all()
#
# PERMISSIONS = {
#     'view': True,
#     'change': lambda u, o: u in get_team(o),
#     'submit': lambda u, o: u in get_team(o),
#     'review': lambda u, o: u in SMT,
#     'approve': lambda u, o: u in SCD,
#     }
#
#
# class PythiaBackend(object):
#     def authenticate(self, **kwargs):
#         return None
#
#     def get_group_permissions(self, user_obj, obj=None):
#         return set()
#
#     def get_all_permissions(self, user_obj, obj=None):
#         return set()
#
#     def has_perm(self, user_obj, perm, obj=None):
#         """Indicate whether a user has the requested permission on an object.
#
#         This method provides business logic on who can "view", "change",
#         "submit", "review" and "approve".
#
#         Hard coded:
#
#         * Users who are not "active" have no permissions.
#         * Superusers have all permissions.
#
#         Through PERMISSIONS:
#
#         * everyone can "view"
#         * project or document team can "change" and "submit"
#         * SMT members can "review" all objects
#         * SCD members can "approve" all objects
#         """
#         if not user_obj.is_active:
#             return False
#         if user_obj.is_superuser:
#             return True
#         # module, perm = perm.split('.', 2)
#         return PERMISSIONS.get(perm, lambda _, __: False)(user_obj, obj)
#
#     def has_module_perms(self, user_obj, app_label):
#         return False
#
#     def get_user(self, user_id):
#         return None


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
