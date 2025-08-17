import json
import asyncio
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from django.conf import settings

import importlib
from robo import Conversation, LoggedConversation
from robo.exceptions import UnknownConversationException

def _get_bot_class():
    import os
    botpath = None
    for k in ('BOTBENCH_BOT', 'BOT'):
        if (botpath := os.getenv(k)) or (botpath := getattr(settings, k)):
            break
    
    if botpath:
        botmodname, botclassname = botpath.rsplit('.', 1)
        botmod = importlib.import_module(botmodname)
        try:
            botclass = getattr(botmod, botclassname)
        except AttributeError as exc:
            raise Exception(f"Bot class '{botclassname}' not found in '{botmodname}'") from exc
        return botclass
    else:
        raise Exception("No bot selected")

def _get_convo_args(bot):
    if hasattr(bot, 'test_argv'):
        return bot.test_argv
    else:
        return []

# settings.BOTBENCH_CHATLOGS_DIR = settings.BASE_DIR / 'chatlogs'

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        
        # Initialize the Anthropic bot for this connection
        self.bot = _get_bot_class()(async_mode=True)
        try:
            self.conversation = LoggedConversation.revive(self.bot, self.conversation_id, settings.BOTBENCH_CHATLOGS_DIR, _get_convo_args(self.bot), stream=True, async_mode=True, cache_user_prompt=True)
        except UnknownConversationException:
            self.conversation = None
        
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        if self.conversation:
            has_soft_started = self.conversation.soft_started and len(self.conversation.messages) > 0
            if self.welcome_message and not has_soft_started:
                welcome = [{'sender': 'ai', 'message': self.welcome_message}]
            else:
                welcome = []
            await self.send(text_data=json.dumps({
                'type': 'revive',
                'chat_history': welcome + [{'sender': 'user' if msg['role'] == 'user' else 'ai', 
                                'message': msg['content'][0]['text']} 
                                for msg in self.conversation.messages if 'text' in msg['content'][0]],
            }))
        else:
            await self.send_welcome_message()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
    
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            user_name = text_data_json.get('user_name', 'User')
            
            # Send user message immediately with client timestamp
            await self.send(text_data=json.dumps({
                'type': 'user_message',
                'message': message,
                'user_name': user_name
            }))
            
            # Get AI response
            await self.get_ai_response(message, user_name)
            
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': f'Error processing message: {str(e)}'
            }))
    
    async def get_ai_response(self, message, user_name):
        try:
            # Initialize conversation if this is the first message
            if self.conversation is None:
                self.conversation = LoggedConversation(self.bot, stream=True, async_mode=True, logs_dir=settings.BOTBENCH_CHATLOGS_DIR, conversation_id=self.conversation_id, cache_user_prompt=True)
                self.conversation.prestart(_get_convo_args(self.bot))
            
            # Send "typing" indicator directly to this connection
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'is_typing': True
            }))
            
            # Send AI message start indicator with client-side timestamp handling
            await self.send(text_data=json.dumps({
                'type': 'ai_start'
            }))
            
            # Get streaming response from Anthropic
            if not self.conversation.started:
                # First message - start the conversation
                stream_wrapper = await self.conversation.astart(message)
            else:
                # Continue existing conversation
                stream_wrapper = await self.conversation.aresume(message)
            
            # Stream the response directly to this connection
            async with stream_wrapper as stream:
                async for chunk in stream.text_stream:
                    # Send each chunk immediately without buffering
                    await self.send(text_data=json.dumps({
                        'type': 'chunk',
                        'chunk': chunk,
                        'sender': 'ai'
                    }))
                    
                    # Small delay to prevent overwhelming the connection
                    await asyncio.sleep(0.01)
            
            # Send completion signal directly
            await self.send(text_data=json.dumps({
                'type': 'complete',
                'sender': 'ai'
            }))
            
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': f"AI Error: {str(e)}"
            }))
        finally:
            # Stop typing indicator directly
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'is_typing': False
            }))
    
    def get_timestamp(self):
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    # WebSocket message handlers
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'sender': event.get('sender', 'user')
        }))
    
    async def chat_chunk(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chunk',
            'chunk': event['chunk'],
            'sender': event['sender']
        }))
    
    async def chat_complete(self, event):
        await self.send(text_data=json.dumps({
            'type': 'complete',
            'sender': event['sender']
        }))
    
    async def chat_typing(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'is_typing': event['is_typing']
        }))
    
    async def chat_error(self, event):
        await self.send(text_data=json.dumps({
            'type': 'error',
            'error': event['error']
        }))
    
    @property
    def welcome_message(self):
        if self.bot.welcome_message is None:
            welcome_text = "Hello! I'm your AI assistant. How can I help you today?"
        elif self.bot.welcome_message == '':
            return
        else:
            welcome_text = self.bot.welcome_message
        return welcome_text
    
    async def send_welcome_message(self):
        
        # Simulate typing
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'is_typing': True
        }))
    
        # Small delay
        await asyncio.sleep(1)
    
        # Start AI message
        await self.send(text_data=json.dumps({
            'type': 'ai_start'
        }))
        
        def chunk_string(s, chunk_size=4):
            return [s[i:i+chunk_size] for i in range(0, len(s), chunk_size)]
        
        # Stream character by character
        for chunk in chunk_string(self.welcome_message):
            await self.send(text_data=json.dumps({
                'type': 'chunk',
                'chunk': chunk,
                'sender': 'ai'
            }))
            await asyncio.sleep(0.06)  # 50ms delay between characters
    
        # Complete the message
        await self.send(text_data=json.dumps({
            'type': 'complete',
            'sender': 'ai'
        }))
    
        # Stop typing
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'is_typing': False
        }))
