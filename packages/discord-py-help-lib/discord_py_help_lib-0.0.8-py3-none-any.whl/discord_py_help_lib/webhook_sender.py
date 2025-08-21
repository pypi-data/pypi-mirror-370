import discord
import traceback
from typing import Union, Optional

async def send_webhook_message(
    channel: Union[discord.TextChannel, discord.VoiceChannel, discord.Thread],
    content: str = None,
    embed: discord.Embed = None,
    embeds: list[discord.Embed] = None,
    username: str = "Webhook Bot",
    avatar_url: str = None,
    file: discord.File = None,
    files: list[discord.File] = None
) -> Optional[discord.WebhookMessage]:
    """
    指定されたチャンネルにWebhookメッセージを送信する
    
    Args:
        channel: 送信先チャンネル (TextChannel/VoiceChannel/Thread)
        content: メッセージ内容
        embed: 埋め込み (単体)
        embeds: 埋め込み (複数)
        username: Webhookの表示名
        avatar_url: Webhookのアイコン画像URL
        file: 添付ファイル (単体)
        files: 添付ファイル (複数)
    
    Returns:
        WebhookMessage: 送信されたメッセージ (失敗時はNone)
    """
    try:
        webhook = None
        target_channel = None
        
        # チャンネルタイプに応じて処理を分岐
        if isinstance(channel, discord.Thread):
            # スレッドの場合、親チャンネルのWebhookを使用
            target_channel = channel.parent
            if not isinstance(target_channel, (discord.TextChannel, discord.VoiceChannel)):
                print(f"Error: スレッドの親チャンネルが無効です: {target_channel}")
                return None
        elif isinstance(channel, discord.VoiceChannel):
            # VCの場合、VCチャットのWebhookを使用
            target_channel = channel
        elif isinstance(channel, discord.TextChannel):
            # テキストチャンネルの場合
            target_channel = channel
        else:
            print(f"Error: サポートされていないチャンネルタイプです: {type(channel)}")
            return None
        
        # 既存のWebhookを検索
        webhooks = await target_channel.webhooks()
        for wh in webhooks:
            if wh.name == "MPEventBot Webhook":
                webhook = wh
                break
        
        # Webhookが存在しない場合は新規作成
        if not webhook:
            try:
                webhook = await target_channel.create_webhook(
                    name="MPEventBot Webhook",
                    reason="MPEventBot用のWebhook"
                )
                print(f"新しいWebhookを作成しました: {target_channel.name}")
            except discord.Forbidden:
                print(f"Error: Webhook作成権限がありません: {target_channel.name}")
                return None
            except discord.HTTPException as e:
                print(f"Error: Webhook作成に失敗しました: {e}")
                return None
        
        # メッセージ送信の準備
        kwargs = {
            "username": username,
            "wait": True  # 送信されたメッセージを取得するため
        }
        
        if avatar_url:
            kwargs["avatar_url"] = avatar_url
        
        if content:
            kwargs["content"] = content
        
        if embed:
            kwargs["embed"] = embed
        elif embeds:
            kwargs["embeds"] = embeds
        
        if file:
            kwargs["file"] = file
        elif files:
            kwargs["files"] = files
        
        # スレッドの場合はthread_idを指定
        if isinstance(channel, discord.Thread):
            kwargs["thread"] = channel
        
        # メッセージ送信
        message = await webhook.send(**kwargs)
        print(f"Webhookメッセージを送信しました: {target_channel.name}")
        return message
        
    except discord.Forbidden:
        print(f"Error: 権限が不足しています: {channel.name if hasattr(channel, 'name') else channel}")
        return None
    except discord.HTTPException as e:
        print(f"Error: HTTP例外が発生しました: {e}")
        return None
    except Exception as e:
        print(f"Error: 予期しないエラーが発生しました: {e}")
        traceback.print_exc()
        return None

async def send_webhook_message_simple(
    channel: Union[discord.TextChannel, discord.VoiceChannel, discord.Thread],
    content: str,
    username: str = "MPEventBot",
    avatar_url: str = None
) -> Optional[discord.WebhookMessage]:
    """
    シンプルなWebhookメッセージ送信 (テキストのみ)
    
    Args:
        channel: 送信先チャンネル
        content: メッセージ内容
        username: Webhookの表示名
        avatar_url: Webhookのアイコン画像URL
    
    Returns:
        WebhookMessage: 送信されたメッセージ (失敗時はNone)
    """
    return await send_webhook_message(
        channel=channel,
        content=content,
        username=username,
        avatar_url=avatar_url
    )

async def send_webhook_embed(
    channel: Union[discord.TextChannel, discord.VoiceChannel, discord.Thread],
    embed: discord.Embed,
    username: str = "MPEventBot",
    avatar_url: str = None
) -> Optional[discord.WebhookMessage]:
    """
    Embed付きWebhookメッセージ送信
    
    Args:
        channel: 送信先チャンネル
        embed: 埋め込み
        username: Webhookの表示名
        avatar_url: Webhookのアイコン画像URL
    
    Returns:
        WebhookMessage: 送信されたメッセージ (失敗時はNone)
    """
    return await send_webhook_message(
        channel=channel,
        embed=embed,
        username=username,
        avatar_url=avatar_url
    )

async def send_webhook_file(
    channel: Union[discord.TextChannel, discord.VoiceChannel, discord.Thread],
    file: discord.File,
    content: str = None,
    username: str = "MPEventBot",
    avatar_url: str = None
) -> Optional[discord.WebhookMessage]:
    """
    ファイル付きWebhookメッセージ送信
    
    Args:
        channel: 送信先チャンネル
        file: 添付ファイル
        content: メッセージ内容 (オプション)
        username: Webhookの表示名
        avatar_url: Webhookのアイコン画像URL
    
    Returns:
        WebhookMessage: 送信されたメッセージ (失敗時はNone)
    """
    return await send_webhook_message(
        channel=channel,
        content=content,
        file=file,
        username=username,
        avatar_url=avatar_url
    )

# 使用例
"""
# テキストチャンネルに送信
channel = bot.get_channel(channel_id)
await send_webhook_message_simple(
    channel=channel,
    content="こんにちは！",
    username="カスタムBot",
    avatar_url="https://example.com/avatar.png"
)

# VCチャットに送信
vc = bot.get_channel(vc_id)
await send_webhook_message_simple(
    channel=vc,
    content="VCチャットメッセージ",
    username="VC Bot"
)

# スレッドに送信
thread = channel.get_thread(thread_id)
await send_webhook_message_simple(
    channel=thread,
    content="スレッドメッセージ",
    username="Thread Bot"
)

# Embed付きで送信
embed = discord.Embed(title="タイトル", description="説明", color=0x00ff00)
await send_webhook_embed(
    channel=channel,
    embed=embed,
    username="Embed Bot",
    avatar_url="https://example.com/avatar.png"
)

# ファイル付きで送信
file = discord.File("path/to/file.txt")
await send_webhook_file(
    channel=channel,
    file=file,
    content="ファイルを送信します",
    username="File Bot"
)
"""
