#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations

import asyncio
import inspect
import logging
from collections import OrderedDict
from typing import Any, Callable, TypeVar, cast

import pyrogram
from pyrogram import utils, types, raw
from pyrogram.handlers import (
    CallbackQueryHandler, MessageHandler, EditedMessageHandler, ErrorHandler, DeletedMessagesHandler,
    UserStatusHandler, RawUpdateHandler, InlineQueryHandler, PollHandler,
    ChosenInlineResultHandler, ChatMemberUpdatedHandler, ChatJoinRequestHandler, StoryHandler
)
from pyrogram.raw.types import (
    UpdateNewMessage, UpdateNewChannelMessage, UpdateNewScheduledMessage,
    UpdateEditMessage, UpdateEditChannelMessage,
    UpdateDeleteMessages, UpdateDeleteChannelMessages,
    UpdateBotCallbackQuery, UpdateInlineBotCallbackQuery,
    UpdateUserStatus, UpdateBotInlineQuery, UpdateMessagePoll,
    UpdateBotInlineSend, UpdateChatParticipant, UpdateChannelParticipant,
    UpdateBotChatInviteRequester, UpdateStory
)

from collections.abc import Awaitable

from pyrogram.handlers.handler import Handler

UpdateType = TypeVar("UpdateType", bound=types.Update)
HandlerType = TypeVar("HandlerType", bound=type["Handler"])
RawUpdateType = TypeVar("RawUpdateType", bound=raw.core.TLObject)

log = logging.getLogger(__name__)


class Dispatcher:
    NEW_MESSAGE_UPDATES = (UpdateNewMessage, UpdateNewChannelMessage, UpdateNewScheduledMessage)
    EDIT_MESSAGE_UPDATES = (UpdateEditMessage, UpdateEditChannelMessage)
    DELETE_MESSAGES_UPDATES = (UpdateDeleteMessages, UpdateDeleteChannelMessages)
    CALLBACK_QUERY_UPDATES = (UpdateBotCallbackQuery, UpdateInlineBotCallbackQuery)
    CHAT_MEMBER_UPDATES = (UpdateChatParticipant, UpdateChannelParticipant)
    USER_STATUS_UPDATES = (UpdateUserStatus,)
    BOT_INLINE_QUERY_UPDATES = (UpdateBotInlineQuery,)
    POLL_UPDATES = (UpdateMessagePoll,)
    CHOSEN_INLINE_RESULT_UPDATES = (UpdateBotInlineSend,)
    CHAT_JOIN_REQUEST_UPDATES = (UpdateBotChatInviteRequester,)
    NEW_STORY_UPDATES = (UpdateStory,)

    def __init__(self, client: pyrogram.Client):
        self.client = client
        self.handler_worker_tasks: list[asyncio.Task] = []
        self.locks_list: list[asyncio.Lock] = []
        self.updates_queue = asyncio.Queue()
        self.groups: dict[int, list[Handler]] = OrderedDict()
        self.error_handlers: list[ErrorHandler] = []
        self._init_update_parsers()

    def _init_update_parsers(self) -> None:
        update_parsers = {
            (
                UpdateNewMessage,
                UpdateNewChannelMessage,
                UpdateNewScheduledMessage,
            ): self._message_parser,
            (UpdateEditMessage, UpdateEditChannelMessage): self._edited_message_parser,
            (UpdateDeleteMessages, UpdateDeleteChannelMessages): self._deleted_messages_parser,
            (UpdateBotCallbackQuery, UpdateInlineBotCallbackQuery): self._callback_query_parser,
            (UpdateUserStatus,): self._user_status_parser,
            (UpdateBotInlineQuery,): self._inline_query_parser,
            (UpdateMessagePoll,): self._poll_parser,
            (UpdateBotInlineSend,): self._chosen_inline_result_parser,
            (UpdateChatParticipant, UpdateChannelParticipant): self._chat_member_updated_parser,
            (UpdateBotChatInviteRequester,): self._chat_join_request_parser,
            (UpdateStory,): self._story_parser,

        }

        self.update_parsers: dict[
            type[raw.core.TLObject],
            Callable[
                ...,
                Awaitable[tuple[types.Update, type[Handler]]] | tuple[types.Update, type[Handler]],
            ],
        ] = {}

        for key_tuple, parser in update_parsers.items():
            for key in key_tuple:
                self.update_parsers[key] = parser

    async def _message_parser(
        self,
        update: UpdateNewMessage,
        users: dict[int, raw.types.User],
        chats: dict[int, raw.types.Chat],
    ) -> tuple[types.Message | None, type[MessageHandler]]:
        return (
            await pyrogram.types.Message._parse(
                client=self.client,
                message=update.message,
                users=users,
                chats=chats,
                is_scheduled=isinstance(update, UpdateNewScheduledMessage),
            ),
            MessageHandler,
        )

    async def _edited_message_parser(
        self,
        update: UpdateNewMessage,
        users: dict[int, raw.types.User],
        chats: dict[int, raw.types.Chat],
    ) -> tuple[types.Message | None, type[EditedMessageHandler]]:
        parsed, _ = await self._message_parser(update, users, chats)
        return parsed, EditedMessageHandler

    def _deleted_messages_parser(
        self,
        update: UpdateDeleteMessages | UpdateDeleteChannelMessages,
        users: dict[int, raw.types.User],
        chats: dict[int, raw.types.Chat],
    ) -> tuple[list[types.Message], type[DeletedMessagesHandler]]:
        return utils.parse_deleted_messages(self.client, update), DeletedMessagesHandler

    async def _callback_query_parser(
        self,
        update: UpdateBotCallbackQuery | UpdateInlineBotCallbackQuery,
        users: dict[int, raw.types.User],
        chats: dict[int, raw.types.Chat],
    ) -> tuple[types.CallbackQuery, type[CallbackQueryHandler]]:
        return await pyrogram.types.CallbackQuery._parse(
            self.client, update, users
        ), CallbackQueryHandler

    def _user_status_parser(
        self,
        update: UpdateUserStatus,
        users: dict[int, raw.types.User],
        chats: dict[int, raw.types.Chat],
    ) -> tuple[types.User, type[UserStatusHandler]]:
        return pyrogram.types.User._parse_user_status(self.client, update), UserStatusHandler

    def _inline_query_parser(
        self,
        update: UpdateBotInlineQuery,
        users: dict[int, raw.types.User],
        chats: dict[int, raw.types.Chat],
    ) -> tuple[types.InlineQuery, type[InlineQueryHandler]]:
        return pyrogram.types.InlineQuery._parse(self.client, update, users), InlineQueryHandler

    def _poll_parser(
        self,
        update: UpdateMessagePoll,
        users: dict[int, raw.types.User],
        chats: dict[int, raw.types.Chat],
    ) -> tuple[types.Poll | None, type[PollHandler]]:
        return pyrogram.types.Poll._parse_update(self.client, update), PollHandler

    def _chosen_inline_result_parser(
        self,
        update: UpdateBotInlineSend,
        users: dict[int, raw.types.User],
        chats: dict[int, raw.types.Chat],
    ) -> tuple[types.ChosenInlineResult, type[ChosenInlineResultHandler]]:
        return pyrogram.types.ChosenInlineResult._parse(
            self.client, update, users
        ), ChosenInlineResultHandler

    def _chat_member_updated_parser(
        self,
        update: UpdateChatParticipant | UpdateChannelParticipant,
        users: dict[int, raw.types.User],
        chats: dict[int, raw.types.Chat],
    ) -> tuple[types.ChatMemberUpdated, type[ChatMemberUpdatedHandler]]:
        return pyrogram.types.ChatMemberUpdated._parse(
            self.client, update, users, chats
        ), ChatMemberUpdatedHandler

    def _chat_join_request_parser(
        self,
        update: UpdateBotChatInviteRequester,
        users: dict[int, raw.types.User],
        chats: dict[int, raw.types.Chat],
    ) -> tuple[types.ChatJoinRequest, type[ChatJoinRequestHandler]]:
        return pyrogram.types.ChatJoinRequest._parse(
            self.client, update, users, chats
        ), ChatJoinRequestHandler

    async def _story_parser(self, update, users, chats):
        return await pyrogram.types.Story._parse(self.client, update.story, users, chats, update.peer), StoryHandler

    async def start(self) -> None:
        if not self.client.no_updates:
            self.locks_list = [asyncio.Lock() for _ in range(self.client.workers)]
            self.handler_worker_tasks = [
                self.client.loop.create_task(self.handler_worker(lock)) for lock in self.locks_list
            ]
            log.info("Started %s HandlerTasks", self.client.workers)

    async def stop(self) -> None:
        if not self.client.no_updates:
            for _ in range(self.client.workers):
                self.updates_queue.put_nowait(None)
            await asyncio.gather(*self.handler_worker_tasks)
            self.handler_worker_tasks.clear()
            self.groups.clear()
            self.error_handlers.clear()

            log.info("Stopped %s HandlerTasks", self.client.workers)

    def add_handler(self, handler: Handler, group: int) -> None:
        if isinstance(handler, ErrorHandler):
            if handler not in self.error_handlers:
                self.error_handlers.append(handler)
        else:
            if group not in self.groups:
                self.groups[group] = []
                self.groups = OrderedDict(sorted(self.groups.items()))
            self.groups[group].append(handler)

    def remove_handler(self, handler: Handler, group: int) -> None:
        if isinstance(handler, ErrorHandler):
            if handler not in self.error_handlers:
                raise ValueError(
                    f"Error handler {handler} does not exist. Handler was not removed."
                )

            self.error_handlers.remove(handler)
        else:
            if group not in self.groups:
                raise ValueError(f"Group {group} does not exist. Handler was not removed.")
            self.groups[group].remove(handler)

    async def handler_worker(self, lock: asyncio.Lock) -> None:
        while True:
            packet = await self.updates_queue.get()
            if packet is None:
                break
            await self._process_packet(packet, lock)
   
    async def _process_packet(
        self,
        packet: tuple[raw.core.TLObject, dict[int, raw.types.User], dict[int, raw.types.Chat]],
        lock: asyncio.Lock,
    ) -> None:
        try:
            update, users, chats = packet
            parser = self.update_parsers.get(type(update))

            if parser is not None:
                parsed_result = parser(update, users, chats)
                if inspect.isawaitable(parsed_result):
                    parsed_update, handler_type = await parsed_result
                else:
                    parsed_update, handler_type = cast(
                        "tuple[types.Update, type[Handler]]", parsed_result
                    )
            else:
                parsed_update = None
                handler_type = None

            await self._process_update(lock, update, users, chats, parsed_update, handler_type)
        except pyrogram.StopPropagation:
            pass
        except Exception as e:
            log.exception(e)
        finally:
            self.updates_queue.task_done()

    async def _process_update(
        self,
        lock: asyncio.Lock,
        raw_update: raw.core.TLObject,
        users: dict[int, raw.types.User],
        chats: dict[int, raw.types.Chat],
        parsed_update: types.Update | None,
        handler_type: type[Handler] | None,
    ) -> None:
        async with lock:
            for group in self.groups.values():
                for handler in group:
                    try:
                        if isinstance(handler, RawUpdateHandler):
                            await self._execute_callback(handler, raw_update, users, chats)
                            continue
                        if (
                            parsed_update is not None
                            and isinstance(handler, handler_type)
                            and await handler.check(self.client, parsed_update)
                        ):
                            await self._execute_callback(handler, parsed_update)
                            break
                    except (pyrogram.StopPropagation, pyrogram.ContinuePropagation) as e:
                        if isinstance(e, pyrogram.StopPropagation):
                            raise
                    except Exception as exception:
                        if parsed_update is not None:
                            await self._handle_exception(parsed_update, exception)

    async def _handle_exception(self, parsed_update: types.Update, exception: Exception) -> None:
        handled_error = False

        for error_handler in self.error_handlers:
            try:
                if await error_handler.check(self.client, parsed_update, exception):
                    handled_error = True
                    break
            except pyrogram.StopPropagation:
                raise
            except pyrogram.ContinuePropagation:
                continue
            except Exception as inner_exception:
                log.exception("Error in error handler: %s", inner_exception)

        if not handled_error:
            log.exception("Unhandled exception: %s", exception)

    async def _execute_callback(self, handler: Handler, *args) -> None:
        if inspect.iscoroutinefunction(handler.callback):
            await handler.callback(self.client, *args)
        else:
            await self.client.loop.run_in_executor(
                self.client.executor, handler.callback, self.client, *args
            )
