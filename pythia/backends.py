from django.contrib.auth import get_user_model


def get_doc_admins(obj):
    return (obj is not None and set((obj.project.project_owner,
                                     obj.project.data_custodian,
                                     obj.project.site_custodian)) or
            set())


def get_doc_reviewers(obj):
    return (obj is not None and set((obj.project.program.program_leader,)) or
            set())


def get_doc_users(obj):
    if obj is not None:
        User = get_user_model()
        pks = obj.project.pythia_membership_project.values_list('user',
                                                                flat=True)
        return set(User.objects.filter(pk__in=pks))
    else:
        return set()


def get_doc_editors(obj):
    # TODO: who is ARAR editors???
    return (obj is not None and set() or set())


PERMISSIONS = {
    'can_submit_for_review': lambda u, o: u in get_doc_admins(o),
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
        # deals with 'documents.can_submit_for_review', 'documents.can_review',
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
