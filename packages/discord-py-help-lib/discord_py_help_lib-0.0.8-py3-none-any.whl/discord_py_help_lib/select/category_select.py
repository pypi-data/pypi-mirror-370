import discord
import traceback
from discord.ext import commands
from typing import Callable, Optional, Awaitable

def select_category(guild: discord.Guild, select_ui_id: str, placeholder: str, page: int = 1, multiselect: bool = False, categories: list[discord.CategoryChannel] = None) -> dict:
    category_list = guild.categories
    if categories:
        category_list = categories
    total_categories = len(category_list)
    
    # 1ページあたりの項目数
    items_per_page = 25
    # ページの範囲を計算
    start = items_per_page * (page - 1)
    end = items_per_page * page
    last_page = (total_categories + items_per_page - 1) // items_per_page  # ページ数を計算
    print(f"start: {start}, end: {end}, total_categories: {total_categories}")
    # 範囲外なら最後のページを選ぶ
    if start >= total_categories:
        start = items_per_page * (last_page - 1)
        end = total_categories
        page = last_page
    options = []
    count: int = 0
    for category in category_list[start:end]:
        options.append(discord.SelectOption(label="📂"+category.name, value=str(category.id)))
        count += 1
    if not multiselect:
        count = 1
    select_ui = discord.ui.Select(custom_id=select_ui_id + "_" + str(page), placeholder=placeholder, options=options, max_values=count)
    return {"select_ui": select_ui, "page": page, "last_page": last_page}

def get_category_select(guild: discord.Guild, select_ui_id: str, placeholder: str, page: int = 1, multiselect: bool = False, categories: list[discord.CategoryChannel] = None) -> discord.ui.View:
    try:
        data = select_category(guild, select_ui_id, placeholder, page, multiselect, categories)
        view: discord.ui.View = discord.ui.View()
        select_category_ui: discord.ui.Select = data["select_ui"]
        view.add_item(select_category_ui)
        prev_button: discord.ui.Button = discord.ui.Button(style=discord.ButtonStyle.red, label="前へ", custom_id=f"{select_ui_id}_back_select_{page - 1}", disabled=False if page > 1 else True)
        view.add_item(prev_button)
        next_button: discord.ui.Button = discord.ui.Button(style=discord.ButtonStyle.green, label="次へ", custom_id=f"{select_ui_id}_next_select_{page + 1}")
        view.add_item(next_button)
        cancel_button: discord.ui.Button = discord.ui.Button(style=discord.ButtonStyle.red, label="キャンセル", custom_id=f"{select_ui_id}_cancel_select")
        view.add_item(cancel_button)
        return view
    except Exception as e:
        print(f"Error in get_category_select: {e}")
        traceback.print_exc()
        return None

class CategorySelectHandler:
    def __init__(self, 
            bot: commands.Bot, 
            custom_id: str,
            placeholder: str = "カテゴリーを選択してください。",
            multiselect: bool = False,
            on_select: Optional[Callable[[discord.Interaction, list[discord.CategoryChannel]], Awaitable[None]]] = None,
            categories: list[discord.CategoryChannel] = None
        ):
        """
        Initialize the CategorySelectHandler.
        
        Args:
            bot: Discord bot instance
            custom_id: Unique identifier for this handler
            placeholder: Placeholder text for the select menu
            multiselect: Whether to allow multiple selections
            on_select: Callback function when categories are selected
        """
        self.bot: commands.Bot = bot
        self.custom_id = custom_id
        self.placeholder = placeholder
        self.multiselect = multiselect
        self.on_select = on_select
        self.categories = categories
    
    def get_custom_id(self) -> str:
        return self.custom_id
    
    def get_view(self, guild: discord.Guild, page: int = 1) -> discord.ui.View:
        return get_category_select(guild, self.custom_id, self.placeholder, page, self.multiselect, self.categories)

    async def call(self, inter: discord.Interaction):
        try:
            custom_id: str = inter.data["custom_id"]
            
            if custom_id == f"{self.custom_id}_cancel_select":
                await inter.response.edit_message(content="キャンセルしました。", view=None)
                    
            elif custom_id.startswith(f"{self.custom_id}_next_select_") or custom_id.startswith(f"{self.custom_id}_back_select_"):
                page: int = int(custom_id.split("_")[-1])
                view = self.get_view(inter.guild, page)
                if not view:
                    await inter.response.edit_message("カテゴリーが設定されていません。", view=None)
                    return
                await inter.response.edit_message(content=f"{self.placeholder}", view=view)
                
            elif custom_id.startswith(f"{self.custom_id}_"):
                # セレクトメニューが選択された場合
                if inter.data.get("component_type") == 3:  # Select Menu
                    selected_ids = inter.data["values"]
                    selected_categories = []
                    for category_id in selected_ids:
                        category = inter.guild.get_channel(int(category_id))
                        if category and isinstance(category, discord.CategoryChannel):
                            selected_categories.append(category)
                    
                    if self.on_select:
                        await self.on_select(inter, selected_categories)
                    else:
                        category_names = [cat.name for cat in selected_categories]
                        await inter.response.edit_message(
                            content=f"選択されたカテゴリー: {', '.join(category_names)}", 
                            view=None
                        )
                        
        except Exception:
            traceback.print_exc()

# グローバルなハンドラー管理辞書
_category_handlers: dict[str, CategorySelectHandler] = {}

def register_category_handler(handler: CategorySelectHandler):
    """ハンドラーを登録"""
    _category_handlers[handler.get_custom_id()] = handler

def get_category_handler(custom_id: str) -> Optional[CategorySelectHandler]:
    """登録されたハンドラーを取得"""
    for handler_id, handler in _category_handlers.items():
        if custom_id.startswith(handler_id):
            return handler
    return None

async def handle_category_interaction(inter: discord.Interaction):
    """統一されたインタラクションハンドラー"""
    custom_id = inter.data["custom_id"]
    handler = get_category_handler(custom_id)
    if handler:
        await handler.call(inter)
    else:
        print("ハンドラーが見つかりません。")
        #await inter.response.send_message("ハンドラーが見つかりません。", ephemeral=True)