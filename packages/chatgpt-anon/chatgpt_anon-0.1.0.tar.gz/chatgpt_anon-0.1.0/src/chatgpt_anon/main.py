#!/usr/bin/python
import requests
from src.chatgpt_anon import helpers
import json
import re
from functools import lru_cache
from typing import Iterator


class ChatGPT:
    def __init__(
        self,
        model: str = "text-davinci-002-render-sha",
        locale: str = "en-US",
        user_agent: str = helpers.request_headers["User-Agent"],
        timeout: tuple = 30,
        disable_history_and_training: bool = False,
    ):
        """Initializes ChatGPT

        Args:
            cookie_path (str): Path to `.json` file containing `chat.openai.com` cookies
            model (str, optional): ChatGPT text generation model name. Defaults to `text-davinci-002-render-sha`.
            conversation_index (int, optional): Conversation index to pick up conversation from. Defaults to `1`.
            locale (str, optional): Your locale. Defaults to `en-US`
            user_agent (str, optional): Http request header User-Agent. Defaults to `Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0`
            timeout (int, optional): Http request timeout.
            trace (bool, optional): Trace websocket requests. Defaults to False.

        """
        self.session = requests.Session()
        self.timeout = timeout
        self.auth = {}  # Will be updated while updating headers
        # self.session.cookies.update(utils.get_cookies(cookie_path))
        self.session.headers.update(
            helpers.get_request_headers_and_initialize_request(self)
        )
        self.conversation_endpoint = "https://chat.openai.com/backend-anon/conversation"
        self.account_detail_endpoint = (
            "https://chat.openai.com/backend-anon/accounts/check"
        )
        self.account_details_endpoint = (
            self.account_detail_endpoint + "/v4-2023-04-27"
        )  # update the date as frequent as possible
        self.prompt_library_endpoint = (
            "https://chat.openai.com/backend-anon/prompt_library/"
        )
        self.previous_conversations_endpoint = (
            "https://chat.openai.com/backend-anon/conversations"
        )
        self.title_generation_endpoint = "https://chat.openai.com/backend-anon/conversation/gen_title/%(conversation_id)s"
        self.conversation_manipulation_endpoint = (
            "https://chat.openai.com/backend-anon/conversation/%(conversation_id)s"
        )
        self.share_conversation_endpoint = (
            "https://chat.openai.com/backend-anon/share/create"
        )
        self.share_conversation_patch_endpoint = (
            "https://chat.openai.com/backend-anon/share/%(share_id)s"
        )
        self.shared_conversations_endpoint = (
            "https://chat.openai.com/backend-anon/shared_conversations"
        )
        self.shared_conversation_view_endpoint = (
            "https://chat.openai.com/share/%(share_id)s"
        )
        self.stop_sharing_conversation_endpoint = (
            "https://chat.openai.com/backend-anon/%(share_id)s"
        )
        self.sentinel_chat_requirements_endpoint: str = (
            "https://chat.openai.com/backend-anon/sentinel/chat-requirements"
        )
        self.session.headers["User-Agent"] = user_agent
        self.locale = locale
        self.model = model
        self.disable_history_and_training = disable_history_and_training
        self.last_response = {}
        self.last_response_metadata = {
            1: {},
            2: {},
        }
        self.__already_init = False
        self.__title_cache = {}
        self.stream_chunk_size = 64

    def __generate_payload(self, prompt: str) -> dict:
        return helpers.generate_payload(self, prompt)

    @property
    def current_conversation_id(self):
        if self.__already_init:
            return self.last_response_metadata.get(2).get("conversation_id")
        else:
            self.__already_init = True
            return None

    def get_current_message_id(self):
        return self.last_response_metadata.get(2).get("message_id")

    def update_sentinel_tokens(self):
        resp = self.session.post(self.sentinel_chat_requirements_endpoint, json={})
        resp.raise_for_status()
        self.session.headers.update(
            {"OpenAI-Sentinel-Chat-Requirements-Token": resp.json()["token"]}
        )

    def ask(
        self,
        prompt: str,
        stream: bool = False,
        raw_response: bool = False,
    ) -> dict | Iterator:
        """Chat with ChatGPT

                Args:
                    prompt (str): message to be send
                    stream (bool, optional): Flag to stream response. Defaults to False.
                    raw_response (bool, optional): Yield back unmodified response
                returns :
                    dict {}
                Yields :
                   Iterator[dict]
        ```json
        {
            "message": {
                "id": "2c98d9ff-495c-4f08-af9e-affbd17xxxxx",
                "author": {
                    "role": "assistant",
                    "name": null,
                    "metadata": {}
                },
                "create_time": 1702666802.823688,
                "update_time": null,
                "content": {
                    "content_type": "text",
                    "parts": [
                        "Of course, your privacy matters! I don't store or remember our conversations once they're completed, so your information is kept confidential. If there's anything specific you'd like to discuss or if you have any concerns, feel free to let me know. I'm here to assist you!"
                    ]
                },
                "status": "finished_successfully",
                "end_turn": true,
                "weight": 1.0,
                "metadata": {
                    "finish_details": {
                        "type": "stop",
                        "stop_tokens": [
                            100260
                        ]
                    },
                    "inline_gizmo_id": null,
                    "is_complete": true,
                    "message_type": "next",
                    "model_slug": "text-davinci-002-render-sha",
                    "parent_id": "7bf27013-a47a-438c-ae17-0ee846b4xxxx",
                    "timestamp_": "absolute"
                },
                "recipient": "all"
            },
            "conversation_id": "affdda8c-588c-4342-9869-26c5bd7xxxxx",
            "error": null
        }
        ```
        """
        payload: dict = self.__generate_payload(prompt)
        # print(json.dumps(payload, indent=4))
        self.update_sentinel_tokens()
        response = self.session.post(
            url=self.conversation_endpoint,
            json=payload,
            timeout=self.timeout,
            stream=True,
        )
        # response.raise_for_status()
        if (
            response.ok
            and response.headers.get("content-type")
            == "text/event-stream; charset=utf-8"
        ):

            def for_stream():
                for value in response.iter_lines(
                    decode_unicode=True,
                    delimiter="data:",
                    chunk_size=self.stream_chunk_size,
                ):
                    try:
                        to_dict = json.loads(value)
                        if "is_completion" in to_dict.keys():
                            # Metadata (response)
                            self.last_response_metadata[
                                2 if to_dict.get("is_completion") else 1
                            ] = to_dict
                            continue
                        # Only data containing the `feedback body` make it to here
                        self.last_response.update(to_dict)
                        yield value if raw_response else to_dict
                    except json.decoder.JSONDecodeError:
                        # Caused by either empty string or [DONE]
                        if raw_response:
                            yield value
                        pass

            def for_non_stream():
                response_to_be_returned = {}
                for value in response.iter_lines(
                    decode_unicode=True,
                    delimiter="data:",
                    chunk_size=self.stream_chunk_size,
                ):
                    try:
                        to_dict = json.loads(value)
                        if "is_completion" in to_dict.keys():
                            # Metadata (response)
                            self.last_response_metadata[
                                2 if to_dict.get("is_completion") else 1
                            ] = to_dict
                            continue
                        # Only data containing the `feedback body` make it to here
                        self.last_response.update(to_dict)
                        response_to_be_returned.update(to_dict)
                    except json.decoder.JSONDecodeError:
                        # Caused by either empty string or [DONE]
                        pass
                return response_to_be_returned

            return for_stream() if stream else for_non_stream()

        else:
            raise Exception(
                f"Failed to fetch response - ({response.status_code}, {response.reason} : {response.headers.get('content-type')} : {response.text})"
            )

    def chat(self, prompt: str, stream: bool = False) -> str:
        """Interact with ChatGPT on the fly

        Args:
            prompt (str): Message to ChatGPT
            stream (bool, optional): Yield the text response. Defaults to False.

        Returns:
            str: Text response generated only

        Yields:
            Iterator[str]: Text response generated only
        """
        resp = self.ask(prompt, stream)

        def for_stream():
            # streaming response
            for response in resp:
                yield helpers.get_message(response)
                # pass  Currently fixed

        def for_non_stream():
            return helpers.get_message(resp)

        return for_stream() if stream else for_non_stream()

    def user_details(self, in_details: bool = True) -> dict:
        """Returns various information concerning the user

                Args:
                    in_details (bool, optional): Return detailed info. Defaults to True.
                returns:
                    dict : {}
        ```json
        {
             "accounts": {
                  "b8a156d7-9a30-4de3-bf40-4d88782xxxxx": {
                       "account": {
                            "account_user_role": "account-owner",
                            "account_user_id": "user-IUW2uKHQ6bwv4bdiI8IYxxxx__b8a156d7-9a30-4de3-bf40-4d887829xxxx",
                            "processor": {
                                 "a001": {
                                      "has_customer_object": false
                                 },
                                 "b001": {
                                      "has_transaction_history": false
                                 },
                                 "c001": {
                                      "has_transaction_history": false
                                 }
                            },
                            "account_id": "b8a156d7-xxxx-4de3-bf40-4d887829xxxx",
                            "organization_id": null,
                            "is_most_recent_expired_subscription_gratis": false,
                            "has_previously_paid_subscription": false,
                            "name": null,
                            "profile_picture_id": null,
                            "profile_picture_url": null,
                            "structure": "personal",
                            "plan_type": "free",
                            "is_deactivated": false,
                            "promo_data": {}
                       },
                       "features": [
                            "allow_url_thread_creation",
                            "arkose_enabled",
                            "arkose_gpt_35_experiment",
                            "bizmo_settings",
                            "breeze_available",
                            "chat_preferences_available",
                            "conversation_bot_arkose",
                            "disable_team_upgrade_ui",
                            "gizmo_live",
                            "gizmo_ui",
                            "invite_referral",
                            "new_plugin_oauth_endpoint",
                            "privacy_policy_nov_2023",
                            "shareable_links",
                            "starter_prompts",
                            "user_settings_announcements"
                       ],
                       "entitlement": {
                            "subscription_id": null,
                            "has_active_subscription": false,
                            "subscription_plan": "chatgptfreeplan",
                            "expires_at": null
                       },
                       "last_active_subscription": {
                            "subscription_id": null,
                            "purchase_origin_platform": "chatgpt_not_purchased",
                            "will_renew": false
                       }
                  },
                  "default": {
                       "account": {
                            "account_user_role": "account-owner",
                            "account_user_id": "user-IUW2uKHQ6bwv4bdiI8IYtjqA__b8a156d7-9a30-4de3-bf40-xxxxxxxxxx",
                            "processor": {
                                 "a001": {
                                      "has_customer_object": false
                                 },
                                 "b001": {
                                      "has_transaction_history": false
                                 },
                                 "c001": {
                                      "has_transaction_history": false
                                 }
                            },
                            "account_id": "b8a156d7-9a30-4de3-bf40-4d887829xxxx",
                            "organization_id": null,
                            "is_most_recent_expired_subscription_gratis": false,
                            "has_previously_paid_subscription": false,
                            "name": null,
                            "profile_picture_id": null,
                            "profile_picture_url": null,
                            "structure": "personal",
                            "plan_type": "free",
                            "is_deactivated": false,
                            "promo_data": {}
                       },
                       "features": [
                            "allow_url_thread_creation",
                            "arkose_enabled",
                            "arkose_gpt_35_experiment",
                            "bizmo_settings",
                            "breeze_available",
                            "chat_preferences_available",
                            "conversation_bot_arkose",
                            "disable_team_upgrade_ui",
                            "gizmo_live",
                            "gizmo_ui",
                            "invite_referral",
                            "new_plugin_oauth_endpoint",
                            "privacy_policy_nov_2023",
                            "shareable_links",
                            "starter_prompts",
                            "user_settings_announcements"
                       ],
                       "entitlement": {
                            "subscription_id": null,
                            "has_active_subscription": false,
                            "subscription_plan": "chatgptfreeplan",
                            "expires_at": null
                       },
                       "last_active_subscription": {
                            "subscription_id": null,
                            "purchase_origin_platform": "chatgpt_not_purchased",
                            "will_renew": false
                       }
                  }
             },
             "account_ordering": [
                  "b8a156d7-9a30-4de3-bf40-4d88782xxxx"
             ]
        }
        ```
        """
        resp = self.session.get(
            (
                self.account_details_endpoint
                if in_details
                else self.account_detail_endpoint
            ),
            timeout=self.timeout,
        )
        return helpers.is_json(resp, "account data")

    def prompt_library(self, limit: int = 4, offset: int = 0) -> list:
        """Generates random prompts

                Args:
                    limit (int, optional): Limit suggestions. Defaults to 4.
                    offset (int, optional): Offset. Defaults to 0.
                returns:
                    list : []

        ```json
           {
            "items": [
                {
                    "id": "edb56xxx",
                    "title": "Design a database schema",
                    "description": "for an online merch store",
                    "prompt": "Design a database schema for an online merch store."
                },
                {
                    "id": "9fa37xxx",
                    "title": "Recommend a dish",
                    "description": "to impress a date who's a picky eater",
                    "prompt": "I'm going to cook for my date who claims to be a picky eater. Can you recommend me a dish that's easy to cook?"
                }
            ],
            "total": 2,
            "limit": 2,
            "offset": 1
            }
        ```
        """

        resp = self.session.get(
            self.prompt_library_endpoint,
            params={"limit": limit, "offset": offset},
            timeout=self.timeout,
        )
        return helpers.is_json(resp, "prompts")

    def previous_conversations(
        self,
        limit: int = 20,
        offset: int = 0,
        order: str = "updated",
        index: int = 1,
        all: bool = False,
    ) -> list:
        """Loads previous conversations

                Args:
                    limit (int, optional): Fetch this specific amount of chats. Defaults to 28.
                    offset (int, optional): ``. Defaults to 0.
                    order (str, optional): Sort order. Defaults to "updated".
                    index (int, optional): Index of the item to be returned +1. Defaults to 1.
                    all (bool, optional): Return all conversations based on specified limit

                Returns:
                    list: Previous conversations contained in dict

                ```json
                {
             "items": [
                  {
                       "id": "86f73b54-0f51-47ba-84a3-07c1e25xxxx",
                       "title": "Urine Cleaning in Rome",
                       "create_time": "2023-12-15T13:39:24.683876+00:00",
                       "update_time": "2023-12-15T14:02:23.776574+00:00",
                       "mapping": null,
                       "current_node": null,
                       "conversation_template_id": null,
                       "gizmo_id": null,
                       "is_archived": false,
                       "workspace_id": null
                  },
                  {
                       "id": "b3779121-8767-4202-9527-3058f40xxxx",
                       "title": "Helpful User, Assistant",
                       "create_time": "2023-12-15T12:03:30.596706+00:00",
                       "update_time": "2023-12-15T13:29:05.286457+00:00",
                       "mapping": null,
                       "current_node": null,
                       "conversation_template_id": null,
                       "gizmo_id": null,
                       "is_archived": false,
                       "workspace_id": null
                  }
             ],
             "total": 108,
             "limit": 2,
             "offset": 0,
             "has_missing_conversations": false
           }
        ```
        """
        assert isinstance(index, int), "Index must be an integer"
        index -= 1  # So that 0 equates to False as in self.current_conversation_id
        resp = self.session.get(
            self.previous_conversations_endpoint,
            params={"limit": limit, "offset": offset, "order": order},
            timeout=self.timeout,
        )
        resp = helpers.is_json(resp, "conversation history")
        if all:
            return resp
        conversations = resp["items"]
        # conversations.reverse()
        if len(conversations) - 1 >= index:
            return conversations[index]
        else:
            raise Exception(
                f"Index '{index} is greater than the total conversations '{len(conversations)}"
            )

    @lru_cache(maxsize=201)
    def generate_title(
        self, conversation_id: str, message_id: str, per_conversation: bool = True
    ) -> dict:
        """Generates title for a particular conversation message

        Args:
            conversation_id (str): ``
            message_id (str): ``
            per_conversation (bool): Ignore message_id and serve from cache based on conversation_id. Defaults to True.

        Returns:
            dict: `{}`
        """
        if per_conversation and self.__title_cache.get(conversation_id):
            # OpenAI dropped support for generating conversation title for every new message in ChatGPT 3.5 model
            #  - Probably to non-premium users only.
            return self.__title_cache[conversation_id]
        resp = self.session.post(
            self.title_generation_endpoint % {"conversation_id": conversation_id},
            json={"message_id": message_id},
            timeout=self.timeout,
        )
        sanitized_resp = helpers.is_json(resp, "title")
        if "message" in sanitized_resp.keys():
            generated_title = sanitized_resp.get("message")
            match = re.search(r"'([^']*)'", generated_title)
            if match:
                sanitized_resp["message"] = match.group(1)
                if per_conversation:
                    self.__title_cache[conversation_id] = sanitized_resp
        return sanitized_resp

    def delete_conversation(self, conversation_id: str) -> dict:
        """Deletes a particular conversation based on ID

        Args:
            conversation_id (str): Conversation iD

        Returns:
            dict: Response
        """
        resp = self.session.patch(
            self.conversation_manipulation_endpoint
            % {"conversation_id": conversation_id},
            json={"is_visible": False},
        )
        return helpers.is_json(resp, "delete")

    def chat_history(self, conversation_id: str, all: bool = False) -> dict:
        """Fetches previous chat prompts and responses

                Args:
                    conversation_id (str): Conversation ID
                    all (bool): Return all response as received. Defaults to False.

                Returns:
                    dict: Previous chats

                ```json
                {
            "title": "Trump's Age Calculator",
            "create_time": 1703074882.684634,
            "update_time": 1703074885.46044,
            "current_node": "f18a446d-8843-4433-acf7-79cb01a8xxxx",
            "conversation_id": "00565704-a7ae-4278-bd14-ca598fedxxxx",
            "is_archived": false,
            "moderation_results": [],
            "safe_urls": [],
            "content": [
                {
                    "author": "User",
                    "create_time": 1703074882.685243,
                    "text": "How old is Donald Triump",
                    "status": "finished_successfully",
                    "id": "aaa2ea97-d8bd-4b93-bff9-09d1a684xxxx"
                },
                {
                    "author": "ChatGPT",
                    "create_time": 1703074884.019059,
                    "text": "Donald Trump was born on June 14, 1946, so his age depends on the current date. If you tell me today's date, I can calculate his age for you!",
                    "status": "finished_successfully",
                    "id": "f18a446d-8843-4433-acf7-79cb01a8xxxx"
                }
            ]
        }
                ```
        """
        resp = self.session.get(
            self.conversation_manipulation_endpoint
            % {"conversation_id": conversation_id}
        )
        from_chatgpt = helpers.is_json(resp, "chat history")
        if all:
            return from_chatgpt
        # title
        # create_time
        # update_time
        # mapping >
        # <Drop first two>
        # mapping > message_id > message > content > parts[0]
        #                                > create_time
        #                                > status
        new_resp = {
            "title": from_chatgpt["title"],
            "create_time": from_chatgpt["create_time"],
            "update_time": from_chatgpt["update_time"],
            "current_node": from_chatgpt["current_node"],
            "conversation_id": from_chatgpt["conversation_id"],
            "is_archived": from_chatgpt["is_archived"],
            "moderation_results": from_chatgpt["moderation_results"],
            "safe_urls": from_chatgpt["safe_urls"],
            "content": [],
        }
        for count, entry in enumerate(list(from_chatgpt["mapping"].keys())[2:]):
            in_need = from_chatgpt["mapping"][entry]["message"]
            new_resp["content"].append(
                {
                    "author": "ChatGPT" if count % 2 else "User",
                    "create_time": in_need["create_time"],
                    "text": in_need["content"]["parts"][0],
                    "status": in_need["status"],
                    "id": entry,
                }
            )
        return new_resp

    def rename_conversation(self, conversation_id: str, title: str) -> dict:
        """Renames conversation title

                Args:
                    conversation_id (str): Conversation ID
                    title (str): New conversation title

                Returns:
                    dict: Success report
                ```json
                {
            "success": true
            }
        ```
        """
        resp = self.session.patch(
            self.conversation_manipulation_endpoint
            % {"conversation_id": conversation_id},
            json={"title": title},
        )
        return helpers.is_json(resp, "rename conversation")

    def archive_conversation(
        self, conversation_id: str, is_archived: bool = True
    ) -> dict:
        """Archives a particular conversation

                Args:
                    conversation_id (str): Conversation ID
                    is_archived (bool): Archive (True) or Unarchive (False). Defaults to `True`.
                Returns:
                    dict: Success report
                ```json
                {
            "success": true
         }
        ```
        """
        resp = self.session.patch(
            self.conversation_manipulation_endpoint
            % {
                "conversation_id": conversation_id,
            },
            json={
                "is_archived": is_archived,
            },
        )
        return helpers.is_json(resp, "archive conversation")

    def share_conversation(
        self,
        conversation_id: str,
        is_anonymous: bool = True,
        is_public: bool = True,
        is_visible: bool = True,
    ) -> dict:
        """Generate link for sharing conversation

                Args:
                    conversation_id (str): Conversation ID
                    anonymous (bool, optional): Hide your Identity in the share. Defaults to True.

                Returns:
                    dict: Success report
                ```json
                {
            "share_id": "a71119f8-9a49-4c1d-b18f-d698313bxxxx",
            "share_url": "https://chat.openai.com/share/a71119f8-9a49-4c1d-b18f-d698313bxxxx",
            "title": "Trump's Age Calculator",
            "is_public": false,
            "is_visible": true,
            "is_anonymous": true,
            "highlighted_message_id": null,
            "current_node_id": "f18a446d-8843-4433-acf7-79cb01a8xxxx",
            "already_exists": false,
            "moderation_state": {
                "has_been_moderated": false,
                "has_been_blocked": false,
                "has_been_accepted": false,
                "has_been_auto_blocked": false,
                "has_been_auto_moderated": false
            }
        }
                ```
        """
        resp = self.session.post(
            self.share_conversation_endpoint,
            json={
                "conversation_id": conversation_id,
                "current_node_id": self.chat_history(conversation_id, True)[
                    "current_node"
                ],
                "is_anonymous": is_anonymous,
            },
        )
        resp_1 = helpers.is_json(resp, "share link")
        resp_2 = self.session.patch(
            self.share_conversation_patch_endpoint % dict(share_id=resp_1["share_id"]),
            json={
                "share_id": resp_1["share_id"],
                "highlighted_message_id": resp_1["highlighted_message_id"],
                "title": resp_1["title"],
                "is_public": is_public,
                "is_visible": is_visible,
                "is_anonymous": is_anonymous,
            },
        )
        resp_1.update(helpers.is_json(resp_2, "patch share link"))
        return resp_1

    def shared_conversations(self, order: str = "created") -> dict:
        """Get previously shared conversations

                Args:
                    order (str, optional): Sorting paran. Defaults to 'created'.

                Returns:
                    dict: Conversations shared
                ```json
            {
            "items": [
                {
                    "id": "57cf604b-37d6-4910-a47c-41xxxxxxxxxx",
                    "title": "Obama's Age: 62 Years",
                    "create_time": "2023-12-20T19:34:47.883282+00:00",
                    "update_time": "2023-12-20T19:44:35+00:00",
                    "mapping": null,
                    "current_node": null,
                    "conversation_template_id": null,
                    "gizmo_id": null,
                    "is_archived": null,
                    "workspace_id": null,
                    "conversation_id": "f8968cc4-8a48-4771-b16c-58xxxxxxxxxx",
                    "url": "https://chat.openai.com/share/57cf604b-37d6-4910-a47c-41xxxxxxxxxx"
                }
            ],
            "total": 10,
            "limit": 50,
            "offset": 0,
            "has_missing_conversations": false
        }


        """
        resp = self.session.get(
            self.shared_conversations_endpoint,
        )
        shareds = helpers.is_json(resp)
        for index, entry in enumerate(shareds["items"]):
            # appends view url to each conversation
            shareds["items"][index]["url"] = (
                self.shared_conversation_view_endpoint % dict(share_id=entry["id"])
            )
        return shareds

    def stop_sharing_conversation(self, share_id: str) -> dict:
        """Deletes sharing link

        Args:
            share_id (str): Shared conversation ID

        Returns:
            dict: Success rate
        """
        resp = self.session.delete(
            self.stop_sharing_conversation_endpoint % dict(share_id=share_id)
        )
        return helpers.is_json(resp, "delete shared conversation")
