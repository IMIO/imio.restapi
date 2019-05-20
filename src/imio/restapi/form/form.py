# -*- coding: utf-8 -*-

from plone import api
from plone.app.textfield import RichText as RichTextField
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone.z3cform.fieldsets.extensible import ExtensibleForm
from plone.z3cform.fieldsets.group import Group
from plone.z3cform.layout import FormWrapper
from plone.z3cform.widget import SingleCheckBoxFieldWidget
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.browser.password import PasswordFieldWidget
from z3c.form.browser.radio import RadioFieldWidget
from z3c.form.browser.select import SelectFieldWidget
from z3c.form.field import Fields
from z3c.form.form import Form
from zope import schema
from zope.interface.interface import InterfaceClass
from zope.schema.vocabulary import SimpleVocabulary
from collective.z3cform.select2.widget.widget import SingleSelect2FieldWidget
from collective.z3cform.select2.widget.widget import MultiSelect2FieldWidget

import requests


class JsonSchema2Z3c(object):
    """
    Convert a json schema to a z3c.form valid schema
    """
    _types_dict = {
        ('string', None): schema.TextLine,
        ('string', 'textarea'): schema.Text,
        ('string', 'richtext'): RichTextField,
        ('string', 'select'): schema.Choice,
        ('string', 'select2'): schema.Choice,
        ('string', 'radio'): schema.Choice,
        ('string', 'checkbox'): schema.Choice,
        ('string', 'multiselect2'): schema.List,
    }

    _widget_dict = {
        'select': SelectFieldWidget,
        'radio': RadioFieldWidget,
        'checkbox': CheckBoxFieldWidget,
        'singlecheckbox': SingleCheckBoxFieldWidget,
        'select2': SingleSelect2FieldWidget,
        'multiselect2': MultiSelect2FieldWidget,
        'wysiwyg': WysiwygFieldWidget,
        'password': PasswordFieldWidget,
    }

    def __init__(self, schema):
        self.schema = schema

    def items(self):
        result = []
        for key, values in self.schema['properties'].items():
            schema_type = self._type_mapping(
                values['type'],
                widget=values.get('widget'),
            )
            properties = self._get_field_properties(key, values)
            result.append((
                str(key),
                schema_type(**properties),
            ))
        return result

    @property
    def generated_schema(self):
        return InterfaceClass(
            'IJson2Z3cSchema',
            attrs={k: v for k, v in self.items()},
        )

    @property
    def generated_groups(self):
        groups = ()
        for fieldset in self.schema['fieldsets'][1:]:
            fields_list = fieldset.get('fields', [])
            fields = Fields(self.generated_schema).select(
                *fields_list
            )
            self._update_fields_widgets(fields, fields_list)
            group_class = type(
                'GeneratedGroup',
                (Group, ),
                {
                    '__name__': fieldset['id'],
                    'fields': fields,
                    'label': fieldset['title'],
                    'description': fieldset.get('description'),
                },
            )
            groups += (group_class, )
        return groups

    @property
    def _default_fields(self):
        if len(self.schema['fieldsets']) > 0:
            return self.schema['fieldsets'][0]['fields']
        return self.schema['properties'].keys()

    @property
    def generated_fields(self):
        fields = Fields(self.generated_schema).select(*self._default_fields)
        self._update_fields_widgets(fields, self._default_fields)
        return fields

    @property
    def form_title(self):
        return self.schema['title']

    def _get_field_properties(self, key, properties):
        f_properties = {
            'title': properties['title'],
            'description': properties.get('description'),
            'required': (key in self.schema.get('required', [])),
        }
        extra_properties = ('vocabulary', 'choices')
        for prop in extra_properties:
            method = getattr(self, '_prop_{0}'.format(prop))
            f_properties.update(method(properties))
        return f_properties

    @staticmethod
    def _prop_vocabulary(properties):
        if 'vocabulary' in properties and properties.get('vocabulary'):
            return {'vocabulary': properties['vocabulary']}
        return {}

    @staticmethod
    def _prop_choices(properties):
        if 'choices' in properties and properties.get('choices'):
            choices = properties['choices']
            if isinstance(choices[0], list) and len(choices[0]) == 2:
                terms = [SimpleVocabulary.createTerm(k, k, v)
                         for k, v in choices]
                return {'vocabulary': SimpleVocabulary(terms)}
            else:
                return {'values': tuple(choices)}
        return {}

    def _type_mapping(self, type, widget=None):
        return self._types_dict.get((type, widget), schema.TextLine)

    def _update_fields_widgets(self, fields, fields_list):
        for fieldname in fields_list:
            f_properties = self.schema['properties'][fieldname]
            widget_factory = self._widget_mapping(f_properties.get('widget'))
            if widget_factory:
                fields[fieldname].widgetFactory = widget_factory
        return fields

    def _widget_mapping(self, widget):
        return self._widget_dict.get(widget)


class BaseForm(ExtensibleForm, Form):
    ignoreContext = True
    _request_schema = 'foo'

    def update(self):
        url = '{0}/@request_schema/{1}'.format(
            api.portal.get().absolute_url(),
            self._request_schema,
        )
        r = requests.get(
            url,
            headers={'Accept': 'application/json'},
            auth=('admin', 'admin')
        )
        if r.status_code == 200:
            converter = JsonSchema2Z3c(r.json())
            self.title = converter.form_title
            self.fields = converter.generated_fields
            self.groups = converter.generated_groups
        super(BaseForm, self).update()


class FormView(FormWrapper):
    form = BaseForm