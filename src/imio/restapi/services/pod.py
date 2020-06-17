# -*- coding: utf-8 -*-

from plone.restapi.interfaces import IExpandableElement
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zope.component import adapter
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface

import pkg_resources


try:
    pkg_resources.get_distribution("collective.documentgenerator")
except pkg_resources.DistributionNotFound:
    HAS_DOCGEN = False
else:
    HAS_DOCGEN = True
    from collective.documentgenerator.interfaces import IGenerablePODTemplates


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class PodTemplates(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            "pod-templates": {
                "@id": "{}/@pod-templates".format(self.context.absolute_url())
            }
        }
        if not expand:
            return result

        # extend batch? DEFAULT_BATCH_SIZE = 25
        # self.request.form['b_size'] = 50

        result = []
        # get generatable POD template for self.context
        adapter = getAdapter(self.context, IGenerablePODTemplates)
        generable_templates = adapter.get_generable_templates()
        context_url = self.context.absolute_url()
        for pod_template in generable_templates:
            serializer = getMultiAdapter((pod_template, self.request), ISerializeToJson)
            serialized = serializer()
            output_formats = pod_template.get_available_formats()
            for output_format in output_formats:
                serialized["generate_url_{0}".format(output_format)] = (
                    context_url
                    + "/document-generation?"
                    + "template_uid={0}&output_format={1}".format(
                        serialized["UID"], output_format
                    )
                )
            result.append(serialized)

        return result


class PodTemplatesGet(Service):
    """ """

    def reply(self):
        pod_templates = PodTemplates(self.context, self.request)
        return pod_templates(expand=True)
