# -*- coding: utf-8 -*-

from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zope.component import getAdapter
from zope.component import getMultiAdapter

import pkg_resources

try:
    pkg_resources.get_distribution('collective.documentgenerator')
except pkg_resources.DistributionNotFound:
    HAS_DOCGEN = False
else:
    HAS_DOCGEN = True
    from collective.documentgenerator.interfaces import IGenerablePODTemplates


class PodTemplatesGet(Service):
    """ """

    def reply(self):
        """ """
        result = {}
        result['pod_templates'] = self.serialize_templates()
        return result

    def serialize_templates(self):
        result = []
        # get generatable POD template for self.context
        adapter = getAdapter(self.context, IGenerablePODTemplates)
        generable_templates = adapter.get_generable_templates()
        context_url = self.context.absolute_url()
        for pod_template in generable_templates:
            serializer = getMultiAdapter(
                (pod_template, self.request), ISerializeToJson)
            serialized = serializer()
            output_formats = pod_template.get_available_formats()
            for output_format in output_formats:
                serialized['generate_url_{0}'.format(output_format)] = \
                    context_url + '/document-generation?template_uid={0}&output_format={1}'.format(
                    serialized['UID'], output_format)
            result.append(serialized)

        return result
