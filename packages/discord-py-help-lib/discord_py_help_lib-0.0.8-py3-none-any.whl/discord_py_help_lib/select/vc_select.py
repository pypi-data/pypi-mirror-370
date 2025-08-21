import discord
import traceback
from discord.ext import commands
from typing import Callable, Optional, Awaitable

def select_vc(guild: discord.Guild, select_ui_id: str, placeholder: str, page: int = 1, multiselect: bool = False, voice_channels: list[discord.VoiceChannel] = None) -> dict:
    # ボイスチャンネルの一覧を取得
    vc_list = [channel for channel in guild.channels if isinstance(channel, discord.VoiceChannel)]
    if voice_channels:
        vc_list = voice_channels
    # カテゴリー順、位置順でソート
    vc_list.sort(key=lambda vc: (vc.category.name if vc.category else "", vc.position))
    
    total_vcs = len(vc_list)
    
    # 1ページあたりの項目数
    items_per_page = 25
    # ページの範囲を計算
    start = items_per_page * (page - 1)
    end = items_per_page * page
    last_page = (total_vcs + items_per_page - 1) // items_per_page  # ページ数を計算
    print(f"start: {start}, end: {end}, total_vcs: {total_vcs}")
    # 範囲外なら最後のページを選ぶ
    if start >= total_vcs:
        start = items_per_page * (last_page - 1)
        end = total_vcs
        page = last_page
    
    options = []
    count: int = 0
    for vc in vc_list[start:end]:
        # カテゴリー名を含めて表示
        if vc.category:
            label = f"🔊[{vc.category.name}] {vc.name}"
        else:
            label = f"🔊{vc.name}"
        
        # ラベルが100文字を超える場合は切り詰める
        if len(label) > 100:
            label = label[:97] + "..."
        
        options.append(discord.SelectOption(label=label, value=str(vc.id)))
        count += 1
    
    if not multiselect:
        count = 1
    
    select_ui = discord.ui.Select(custom_id=select_ui_id + "_" + str(page), placeholder=placeholder, options=options, max_values=count)
    return {"select_ui": select_ui, "page": page, "last_page": last_page}

def get_vc_select(guild: discord.Guild, select_ui_id: str, placeholder: str, page: int = 1, multiselect: bool = False, voice_channels: list[discord.VoiceChannel] = None) -> discord.ui.View:
    try:
        data = select_vc(guild, select_ui_id, placeholder, page, multiselect, voice_channels)
        view: discord.ui.View = discord.ui.View()
        select_vc_ui: discord.ui.Select = data["select_ui"]
        view.add_item(select_vc_ui)
        
        page = data["page"]
        last_page = data["last_page"]
        
        prev_button: discord.ui.Button = discord.ui.Button(
            style=discord.ButtonStyle.red, 
            label="前へ", 
            custom_id=f"{select_ui_id}_back_select_{page - 1}", 
            disabled=page <= 1
        )
        view.add_item(prev_button)
        
        next_button: discord.ui.Button = discord.ui.Button(
            style=discord.ButtonStyle.green, 
            label="次へ", 
            custom_id=f"{select_ui_id}_next_select_{page + 1}",
            disabled=page >= last_page
        )
        view.add_item(next_button)
        
        cancel_button: discord.ui.Button = discord.ui.Button(
            style=discord.ButtonStyle.red, 
            label="キャンセル", 
            custom_id=f"{select_ui_id}_cancel_select"
        )
        view.add_item(cancel_button)
        
        return view
    except Exception as e:
        print(f"Error in get_vc_select: {e}")
        traceback.print_exc()
        return None

class VCSelectHandler:
    def __init__(self, 
            bot: commands.Bot, 
            custom_id: str,
            placeholder: str = "ボイスチャンネルを選択してください。",
            multiselect: bool = False,
            on_select: Optional[Callable[[discord.Interaction, list[discord.VoiceChannel]], Awaitable[None]]] = None,
            voice_channels: list[discord.VoiceChannel] = None
        ):
        """
        Initialize the VCSelectHandler.
        
        Args:
            bot: Discord bot instance
            custom_id: Unique identifier for this handler
            placeholder: Placeholder text for the select menu
            multiselect: Whether to allow multiple selections
            on_select: Callback function when voice channels are selected
        """
        self.bot: commands.Bot = bot
        self.custom_id = custom_id
        self.placeholder = placeholder
        self.multiselect = multiselect
        self.on_select = on_select
        self.voice_channels = voice_channels
    
    def get_custom_id(self) -> str:
        return self.custom_id
    
    def get_view(self, guild: discord.Guild, page: int = 1) -> discord.ui.View:
        return get_vc_select(guild, self.custom_id, self.placeholder, page, self.multiselect, self.voice_channels)

    async def call(self, inter: discord.Interaction):
        try:
            custom_id: str = inter.data["custom_id"]
            
            if custom_id == f"{self.custom_id}_cancel_select":
                await inter.response.edit_message(content="キャンセルしました。", view=None)
                    
            elif custom_id.startswith(f"{self.custom_id}_next_select_") or custom_id.startswith(f"{self.custom_id}_back_select_"):
                page: int = int(custom_id.split("_")[-1])
                view = self.get_view(inter.guild, page)
                if not view:
                    await inter.response.edit_message("ボイスチャンネルが設定されていません。", view=None)
                    return
                await inter.response.edit_message(content=f"{self.placeholder}", view=view)
                
            elif custom_id.startswith(f"{self.custom_id}_"):
                # セレクトメニューが選択された場合
                if inter.data.get("component_type") == 3:  # Select Menu
                    selected_ids = inter.data["values"]
                    selected_vcs = []
                    for vc_id in selected_ids:
                        vc = inter.guild.get_channel(int(vc_id))
                        if vc and isinstance(vc, discord.VoiceChannel):
                            selected_vcs.append(vc)
                    
                    if self.on_select:
                        await self.on_select(inter, selected_vcs)
                    else:
                        vc_names = [vc.name for vc in selected_vcs]
                        await inter.response.edit_message(
                            content=f"選択されたボイスチャンネル: {', '.join(vc_names)}", 
                            view=None
                        )
                        
        except Exception:
            traceback.print_exc()

# グローバルなハンドラー管理辞書
_vc_handlers: dict[str, VCSelectHandler] = {}

def register_vc_handler(handler: VCSelectHandler):
    """ハンドラーを登録"""
    _vc_handlers[handler.get_custom_id()] = handler

def get_vc_handler(custom_id: str) -> Optional[VCSelectHandler]:
    """登録されたハンドラーを取得"""
    for handler_id, handler in _vc_handlers.items():
        if custom_id.startswith(handler_id):
            return handler
    return None

async def handle_vc_interaction(inter: discord.Interaction):
    """統一されたインタラクションハンドラー"""
    custom_id = inter.data["custom_id"]
    handler = get_vc_handler(custom_id)
    if handler:
        await handler.call(inter)
    else:
        print("ハンドラーが見つかりません。")
        #await inter.response.send_message("ハンドラーが見つかりません。", ephemeral=True)