from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from django import forms
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.forms import (PasswordResetForm, UserCreationForm,
                                       UserChangeForm)
from django.utils.html import format_html_join, format_html
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from datetime import datetime


class TermsAndConditionsForm(forms.Form):
    first_name = forms.CharField(
        label="First name",
        error_messages={"required": "First name cannot be blank."})
    last_name = forms.CharField(
        label="Last name",
        error_messages={"required": "Last name cannot be blank."})
    agree = forms.BooleanField(
        required=True, initial=False,
        help_text="Do you agree to the terms and conditions?",
        label="I agree",
        error_messages={
            "required": "You must agree to the terms and conditions."})


class TransitionForm(forms.Form):
    email_notifications = forms.BooleanField(
        required=False, initial=True,
        label="Notify relevant stakeholders by email"
    )


class BaseInlineEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BaseInlineEditForm, self).__init__(*args, **kwargs)
        # hack the form into its widget(s) so that the widget(s) can access (in
        # its render method) form.instance to figure out the ajax url
        for field in self.fields.keys():
            self.fields[field].widget.form = self


class SdisErrorList(forms.util.ErrorList):
    # custom error classes
    def as_ul(self):
        if not self:
            return ''
        return format_html(
            '<ul class="errorlist alert alert-block alert-error fade in">'
            '{0}</ul>', format_html_join('', '<li>{0}</li>',
                                         ((force_text(e),) for e in self)
                                         )
        )


class SdisModelForm(forms.models.ModelForm):
    # custom error_class for modelforms created by .get_changelist_formset
    def __init__(self, *args, **kwargs):
        kwargs['error_class'] = SdisErrorList
        super(SdisModelForm, self).__init__(*args, **kwargs)

    def has_changed(self):
        """
        The shadow/initial date objects use hidden fields that have no idea
        about dates so their values (unlike the display values) are always in
        the isoformat 'YYYY-MM-DD' as returned by datetime.date.__str__()
        http://docs.python.org/2/library/datetime.html#datetime.date.__str__
        let's help it a little bit and try to convert those shadow/initial
        date strings into the (possibly) custom formatted strings so that our
        untouched forms don't get treated as if they were touched.
        see PBS-913.
        It appears this has been fixed in django 1.6 where the
        widget._has_changed has been deprecated in favour of
        field._has_changed.
        https://code.djangoproject.com/ticket/16612
        which means this could probably be refactored/simplified to use
        field.to_python() instead of datetime.strptime() but I guess we'll
        wait for django 1.6 :)
        """
        if self._changed_data is None:
            self._changed_data = self.changed_data
            if bool(self._changed_data):
                for index, name in enumerate(self._changed_data):
                    field = self.fields[name]
                    if (field.show_hidden_initial and
                            field.__class__.__name__ == 'DateField'):
                        prefixed_name = self.add_prefix(name)
                        initial_prefixed_name = self.add_initial_prefix(name)
                        data_value = field.widget.value_from_datadict(
                            self.data, self.files, prefixed_name)
                        hidden_widget = field.hidden_widget()
                        initial_value = hidden_widget.value_from_datadict(
                            self.data, self.files, initial_prefixed_name)
                        try:
                            date = datetime.strptime(initial_value,
                                                     "%Y-%m-%d").date()
                        except ValueError:
                            pass
                        else:
                            initial_value = field.widget._format_value(date)

                        if not field.widget._has_changed(initial_value,
                                                         data_value):
                            self._changed_data.pop(index)
        return bool(self._changed_data)


class WideTextarea(forms.Textarea):
    """
    Add span8 class to the stock Textarea widget, to make it full-width.
    """
    def __init__(self, *args, **kwargs):
        self.attrs = {'class': 'span8'}


class BaseFormHelper(FormHelper):
    """
    Base helper class for rendering forms via crispy_forms.
    To remove the default "Save" button from the helper, instantiate it with
    inputs=[]
    E.g. helper = BaseFormHelper(inputs=[])
    """
    def __init__(self, *args, **kwargs):
        super(BaseFormHelper, self).__init__(*args, **kwargs)
        self.form_class = 'form-horizontal'
        self.help_text_inline = True
        self.form_method = 'POST'
        save_btn = Submit('submit', 'Save')
        save_btn.field_classes = 'btn btn-primary'
        self.add_input(save_btn)


class HelperModelForm(forms.ModelForm):
    """
    Stock ModelForm with a property named ``helper`` (used by crispy_forms to
    render in templates).
    """
    @property
    def helper(self):
        helper = BaseFormHelper()
        return helper


class SdisAdminAuthenticationForm(AdminAuthenticationForm):
    """
    A custom authentication form used in the offsets internal application.
    Subclasses the form in django.contrib.admin.forms because that form will
    test is_staff==True for all logins in its clean() method.
    We need to be able to have internal users login to the application without
    manually setting is_staff to True.
    """
    ERROR_MESSAGE = _("Please enter the correct %(username)s and password "
                      "for a staff account. Note that both fields may be "
                      "case-sensitive.")

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        message = self.ERROR_MESSAGE

        if username and password:
            self.user_cache = authenticate(username=username,
                                           password=password)
            if self.user_cache is None:
                raise forms.ValidationError(message % {
                    'username': self.username_field.verbose_name
                })
        self.check_for_test_cookie()
        return self.cleaned_data


class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['is_active'].label = ("Approved User (i.e. enable login "
                                          "for this user?)")
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['username'].widget.attrs['readonly'] = True
            self.fields['email'].widget.attrs['readonly'] = True
            self.fields['first_name'].widget.attrs['readonly'] = True
            self.fields['last_name'].widget.attrs['readonly'] = True

    class Meta:
        model = User
        fields = ('is_active', 'groups')


# shim around django-admin forms broken by custom user object
# see django ticket #19353
class PythiaUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            self.Meta.model.objects.get(username=username)
        except self.Meta.model.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])


class PythiaUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = get_user_model()



class SdisPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        kwargs['error_class'] = SdisErrorList
        super(SdisPasswordResetForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        # ensure this is an FPC email
        email = self.cleaned_data['email']
        #if not email.lower().endswith(settings.FPC_EMAIL_EXT):
        #    raise forms.ValidationError(
        #        _("This is not a valid FPC email address. " +
        #          "Only FPC users can reset their password " +
        #          "via this interface"))
        return super(SdisPasswordResetForm, self).clean_email()
