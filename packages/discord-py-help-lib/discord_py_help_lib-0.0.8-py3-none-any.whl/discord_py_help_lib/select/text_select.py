import discord
import traceback
from discord.ext import commands
from typing import Callable, Optional, Awaitable

def select_text_dict(
    label_value_dict: dict[str, str],
    select_ui_id: str,
    placeholder: str,
    page: int = 1,
    multiselect: bool = False
) -> dict:
    items = list(label_value_dict.items())
    total_items = len(items)

    items_per_page = 25
    start = items_per_page * (page - 1)
    end = items_per_page * page
    last_page = (total_items + items_per_page - 1) // items_per_page

    if start >= total_items:
        start = items_per_page * (last_page - 1)
        end = total_items
        page = last_page

    options = []
    for label, value in items[start:end]:
        if len(label) > 100:
            label = label[:97] + "..."
        options.append(discord.SelectOption(label=label, value=value))

    max_values = len(options) if multiselect else 1
    select_ui = discord.ui.Select(
        custom_id=f"{select_ui_id}_{page}",
        placeholder=placeholder,
        options=options,
        max_values=max_values
    )

    return {"select_ui": select_ui, "page": page, "last_page": last_page}


def get_text_dict_select(
    label_value_dict: dict[str, str],
    select_ui_id: str,
    placeholder: str,
    page: int = 1,
    multiselect: bool = False
) -> discord.ui.View:
    data = select_text_dict(label_value_dict, select_ui_id, placeholder, page, multiselect)
    view = discord.ui.View()
    view.add_item(data["select_ui"])

    page = data["page"]
    last_page = data["last_page"]

    prev_button = discord.ui.Button(
        style=discord.ButtonStyle.red,
        label="前へ",
        custom_id=f"{select_ui_id}_back_select_{page - 1}",
        disabled=page <= 1
    )
    next_button = discord.ui.Button(
        style=discord.ButtonStyle.green,
        label="次へ",
        custom_id=f"{select_ui_id}_next_select_{page + 1}",
        disabled=page >= last_page
    )
    cancel_button = discord.ui.Button(
        style=discord.ButtonStyle.red,
        label="キャンセル",
        custom_id=f"{select_ui_id}_cancel_select"
    )

    view.add_item(prev_button)
    view.add_item(next_button)
    view.add_item(cancel_button)

    return view


class TextSelectHandler:
    def __init__(
        self,
        bot: commands.Bot,
        label_value_dict: dict[str, str],
        custom_id: str,
        placeholder: str = "項目を選択してください。",
        multiselect: bool = False,
        on_select: Optional[Callable[[discord.Interaction, list[str]], Awaitable[None]]] = None,
    ):
        """
        Args:
            bot: Discord bot instance
            label_value_dict: {label: value} の辞書
            custom_id: Unique identifier for this handler
            placeholder: セレクトメニューのプレースホルダー
            multiselect: 複数選択可能か
            on_select: 選択時のコールバック (interaction, 選択されたvalueリスト)
        """
        self.bot = bot
        self.data_dict = label_value_dict
        self.custom_id = custom_id
        self.placeholder = placeholder
        self.multiselect = multiselect
        self.on_select = on_select

    def get_custom_id(self) -> str:
        return self.custom_id

    def get_view(self, page: int = 1) -> discord.ui.View:
        return get_text_dict_select(self.data_dict, self.custom_id, self.placeholder, page, self.multiselect)

    async def call(self, inter: discord.Interaction):
        try:
            custom_id: str = inter.data["custom_id"]

            if custom_id == f"{self.custom_id}_cancel_select":
                await inter.response.edit_message(content="キャンセルしました。", view=None)

            elif custom_id.startswith(f"{self.custom_id}_next_select_") or custom_id.startswith(f"{self.custom_id}_back_select_"):
                page: int = int(custom_id.split("_")[-1])
                view = self.get_view(page)
                await inter.response.edit_message(content=f"{self.placeholder}", view=view)

            elif custom_id.startswith(f"{self.custom_id}_"):
                if inter.data.get("component_type") == 3:  # Select Menu
                    selected_values = inter.data["values"]
                    if self.on_select:
                        await self.on_select(inter, selected_values)
                    else:
                        await inter.response.edit_message(
                            content=f"選択された項目: {', '.join(selected_values)}",
                            view=None
                        )

        except Exception:
            traceback.print_exc()


# ハンドラー管理
_text_handlers: dict[str, TextSelectHandler] = {}

def register_text_handler(handler: TextSelectHandler):
    _text_handlers[handler.get_custom_id()] = handler

def get_text_handler(custom_id: str) -> Optional[TextSelectHandler]:
    for handler_id, handler in _text_handlers.items():
        if custom_id.startswith(handler_id):
            return handler
    return None

async def handle_text_interaction(inter: discord.Interaction):
    try:
        custom_id = inter.data["custom_id"]
        handler = get_text_handler(custom_id)
        if handler:
            await handler.call(inter)
        else:
            print("ハンドラーが見つかりません。")
    except Exception:
        traceback.print_exc()