from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.clickjacking import xframe_options_exempt

import uuid


@xframe_options_exempt
def conversation_embed(request, conversation_id):
    config = {'conversation_config': {'conversation_id': conversation_id}}
    return render(request, 'chat/chat_embed.html', config)


@xframe_options_exempt
def conversation_new(request):
    new_conversation_id = str(uuid.uuid4())
    return HttpResponseRedirect(reverse('conversation', args=[new_conversation_id]))


def embed_example(request):
    return render(request, 'chat/embed_example.html', {})
