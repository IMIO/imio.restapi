# -*- coding: utf-8 -*-

from plone import api
from plone.restapi.deserializer import json_body
from plone.restapi.services.content import add
from ZPublisher.HTTPRequest import HTTPRequest

import json


def create_request(base_request, body):
    request = HTTPRequest(
        base_request.stdin,
        base_request._orig_env,
        base_request.response,
    )
    for attr in base_request.__dict__.keys():
        setattr(request, attr, getattr(base_request, attr))
    request.set('BODY', body)
    return request


class FolderPost(add.FolderPost):

    def _prepare_data(self, data):
        '''Hook to manipulate the data structure if necessary.'''
        return data

    def _after_reply_hook(self, serialized_obj):
        '''Hook to be overrided if necessary.'''
        return

    def _wf_transition_additional_warning(self, tr):
        '''Hook to add some specific context for
           transition not triggerable warning.'''
        return ''

    def wf_transitions(self, serialized_obj):
        '''If a key 'wf_transitions' is there, try to trigger it.'''
        wf_tr = self.data.get('wf_transitions', [])
        if not wf_tr:
            return
        with api.env.adopt_roles(roles=['Manager']):
            wfTool = api.portal.get_tool('portal_workflow')
            wf_comment = u'wf_transition_triggered_by_application'
            obj = self.context.get(serialized_obj['id'])
            for tr in wf_tr:
                available_transitions = [t['id'] for t in wfTool.getTransitionsFor(obj)]
                if tr not in available_transitions:
                    warning_message = "While treating wfTransitions, could not " \
                        "trigger the '{0}' transition!".format(tr)
                    warning_message += self._wf_transition_additional_warning(tr)
                    self.warnings.append(warning_message)
                    continue
                # we are sure transition is available, trigger it
                wfTool.doActionFor(obj, tr, comment=wf_comment)

    def reply(self):
        data = json_body(self.request)
        children = []
        data = self._prepare_data(data)
        if '__children__' in data:
            children = data.pop('__children__')
            self.request.set('BODY', json.dumps(data))
        result = super(FolderPost, self).reply()
        self._after_reply_hook(result)
        self.wf_transitions(result)
        if children:
            results = []
            for child in children:
                context = self.context.get(result['id'])
                child_data = self._prepare_data(child)
                request = create_request(self.request, json.dumps(child_data))
                child_request = self.__class__(context, request)
                child_request.context = context
                child_request.request = request
                results.append(child_request.reply())
            result['__children__'] = results
        return result


class BulkFolderPost(FolderPost):

    def reply(self):
        data = json_body(self.request)
        result = []
        for element in data['data']:
            self.request.set('BODY', json.dumps(element))
            result.extend(super(BulkFolderPost, self).create_content())
        return {'data': result}
