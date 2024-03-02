#——————————
# DEVELOPERS: darkness800, youbanan
# QUICKAI 2023-2024
#——————————

import asyncio
import disnake
from disnake.ext import commands
import openai
import os
import random
import re
import aiohttp
import sqlite3
from datetime import datetime, timedelta
import math
import json
import pytz
import io
import deep_translator
from deep_translator import GoogleTranslator
import time
import requests

intents = disnake.Intents.default()
intents.messages = True
intents.typing = True
intents.message_content = True

bot = commands.Bot(command_prefix="&", intents=intents, help_command=None)

# Список API ключей
api_keys = [
    "OpenAI API key",
]
  
# установка статуса
@bot.event
async def on_ready():
    info = "!"
    print("[{}] Бот готов к работе.".format(info)) 
    while True:
        guild_count = len(bot.guilds)
        activity = disnake.Activity(name=f'for {guild_count} guilds', type=disnake.ActivityType.watching)
        activity1 = disnake.Activity(name=f'for {sum(guild.member_count for guild in bot.guilds)} users', type=disnake.ActivityType.watching)
        await bot.change_presence(status=disnake.Status.idle, activity=activity)
        await asyncio.sleep(3) 
        await bot.change_presence(status=disnake.Status.idle, activity=activity1)
        await asyncio.sleep(3)

# Логирование инвайтов
@bot.event
async def on_guild_join(guild):
        channell = bot.get_channel(1177291247912767585)
        guild_count = len(bot.guilds)
        creator = await bot.fetch_user(guild.owner_id)
        embedd = disnake.Embed(title=f"<:plus:1185004396522778625> QuickAI добавлен на сервер {guild.name}",
                          colour=0xffffff,
                          timestamp=datetime.now())

        embedd.set_author(name=f"Владелец сервера: {creator.name}")

        embedd.add_field(name="О сервере",
                    value=f"{guild.name} [(аватар)](xyi znaet) | {guild.id} (ID)",
                    inline=False)
        embedd.add_field(name="Владелец (ID)",
                    value=f"{guild.owner_id}",
                    inline=False)
        embedd.add_field(name="Количество участников",
                    value=f"{guild.member_count}",
                    inline=False)

        embedd.set_footer(text=f"Текущее количество серверов: {guild_count}")
        await channell.send(embed=embedd)

# Обработчик ошибок  
@bot.event
async def on_slash_command_error(ctx, error):
    locale = {
        "permissions": {
            "create_instant_invite": "Создавать приглашения",
            "kick_members": "Выгонять участников",
            "ban_members": "Банить участников",
            "administrator": "Администратор",
            "manage_channels": "Управлять каналами",
            "manage_guild": "Управлять сервером",
            "add_reactions": "Добавлять реакции",
            "view_audit_log": "Просматривать журнал аудита",
            "manage_messages": "Управлять сообщениями",
            "embed_links": "Прикреплять ссылки",
            "attach_files": "Прикреплять файлы",
            "read_message_history": "Читать историю сообщений",
            "mention_everyone": "Упоминать всех",
            "external_emojis": "Использовать внешние эмодзи",
            "connect": "Подключаться к голосовым каналам",
            "speak": "Говорить в голосовых каналах",
            "move_members": "Перемещать участников",
            "change_nickname": "Изменять никйнейм",
            "manage_nicknames": "Управлять никнеймами",
            "manage_roles": "Управлять ролями",
            "manage_webhooks": "Управлять вебхуками",
            "manage_emojis": "Управлять эмодзи",
            "moderate_members": "Модерировать участников",
        }
    }
    if isinstance(error, commands.CommandOnCooldown):
        retry_after = str(datetime.datetime(seconds=error.retry_after)).split('.')[0]
        embed = disnake.Embed(
            title="<:n_error:1185671987859828836> Ошибка",
            description=f"К сожалению, но для того, чтобы выполнить снова данную команду, подождите **{retry_after}** минут/секунд!",
            color=0xffffff
        )
        await ctx.send(embed=embed, ephemeral=True)
    if isinstance(error, commands.MissingPermissions):
        perms = [
            f'— **{locale["permissions"][perm]}**'
            for perm in error.missing_permissions
        ]
        embed = disnake.Embed(
            title="<:n_error:1185671987859828836> Ошибка",
            description=f"К сожалению, но у Вас недостаточно прав для выполнения данной команды! Необходимые права: \n" + "\n".join(perms),
            color=0xffffff
        )
        await ctx.send(embed=embed, ephemeral=True)
    if isinstance(error, commands.BotMissingPermissions):
        perms = [
            f'— **{locale["permissions"][perm]}**'
            for perm in error.missing_permissions
        ]
        embed = disnake.Embed(
            title="<:n_error:1185671987859828836> Ошибка",
            description=f"К сожалению, но у меня недостаточно прав для выполнения данной команды! Необходимые права: \n" + "\n".join(perms),
            color=0xffffff
        )
        await ctx.send(embed=embed, ephemeral=True)


  
# ——————
# Функции
# ——————

# Получение рандом ключа на запрос
def get_random_api_key():
    return random.choice(api_keys)    
    
# Установка канала для общения без пингов
@bot.slash_command(name='without-mentioning', description='Set the channel for dialog with the bot without mentioning.', options=[disnake.Option('channel', 'Select a channel.', type=disnake.OptionType.channel, required=False)])
@commands.has_permissions(administrator=True)
async def set_bot_channel(ctx, channel: disnake.TextChannel = None):
    conn = sqlite3.connect('language.db')
    c = conn.cursor()
    c.execute("SELECT language FROM settings WHERE guild_id=?", (ctx.guild.id,))
    result = c.fetchone()
    language = result[0] if result else "Russian"
    conn.close()

    if language == 'English':
        embed_error = disnake.Embed(
            title="<:n_error:1185671987859828836> Error",
            description="You are blacklisted!",
            color=0xffffff
        )
        embed_success = disnake.Embed(
            title='<:n_succes:1185671944004194375> Success',
            description='The channel was successfully set!',
            color=0xffffff
        )
    else:
        embed_error = disnake.Embed(
            title="<:n_error:1185671987859828836> Ошибка",
            description="Вы находитесь в черном списке!",
            color=0xffffff
        )
        embed_success = disnake.Embed(
            title='<:n_succes:1185671944004194375> Успешно',
            description='Канал был успешно установлен!',
            color=0xffffff
        )

    guild_id = ctx.guild.id

    if await is_blocked_user(ctx.author.id):
        components = [
            disnake.ui.Button(label="Support server", style=disnake.ButtonStyle.url, url="https://dsc.gg/quickai")
        ]
        await ctx.send(embed=embed_error, ephemeral=True, components=components)
    else:
        if channel is None:
            cursor.execute('''
                DELETE FROM bot_channels WHERE guild_id=? AND channel_id=?
            ''', (guild_id, ctx.channel.id))
            db.commit()

            await ctx.send(embed=embed_success)
        else:
            cursor.execute('''
                INSERT OR REPLACE INTO bot_channels(guild_id, channel_id) VALUES(?,?)
            ''', (guild_id, channel.id))
            db.commit()

            await ctx.send(embed=embed_success)
       
        
# Скачать диалог        
@bot.slash_command(
    description="Download the dialog in txt format."
)
async def download_dialog(ctx):
    conn = sqlite3.connect('language.db')
    c = conn.cursor()
    c.execute("SELECT language FROM settings WHERE guild_id=?", (ctx.guild.id,))
    result = c.fetchone()
    language = result[0] if result else "Russian"
    conn.close()

    if language == 'English':
        embed_error = disnake.Embed(
            title="<:n_error:1185671987859828836> Error",
            description="You are blacklisted!",
            color=0xffffff
        )
        embed_no_history = disnake.Embed(
            title='<:n_error:1185671987859828836> Error',
            description='Unfortunately, you have no dialog history!',
            color=0xffffff
        )
    else:
        embed_error = disnake.Embed(
            title="<:n_error:1185671987859828836> Ошибка",
            description="Вы находитесь в черном списке!",
            color=0xffffff
        )
        embed_no_history = disnake.Embed(
            title='<:n_error:1185671987859828836> Ошибка',
            description='К сожалению, но у вас нету истории диалога!',
            color=0xffffff
        )

    if await is_blocked_user(ctx.author.id):
        components = [
            disnake.ui.Button(label="Support server", style=disnake.ButtonStyle.url, url="https://dsc.gg/quickaibot")
        ]
        await ctx.send(embed=embed_error, ephemeral=True, components=components)
    else:
        dialog_id = f"dialog-{ctx.author.id}"
        filename = f"{dialog_id}.txt"
        if os.path.exists(filename):
            with open(filename, "r") as file:
                dialog_content = file.read()
            file = disnake.File(filename, filename="dialog.txt")
            await ctx.send(file=file, ephemeral=True)
        else:
            await ctx.send(embed=embed_no_history, ephemeral=True)
        
# Добавление кастом промптов  
@bot.slash_command(name='prompt', description='Set the bot communication rule.', options=[disnake.Option('text', 'Text of your rule.', required=True)])
async def prompt(ctx, text: str):
    conn = sqlite3.connect('language.db')
    c = conn.cursor()
    c.execute("SELECT language FROM settings WHERE guild_id=?", (ctx.guild.id,))
    result = c.fetchone()
    language = result[0] if result else "Russian"  # Если язык не указан, используется английский
    conn.close()

    if language == 'English':
        embed = disnake.Embed(title='<:n_succes:1185671944004194375> Successfully', description='The rule has been added.\n\n To reset it, use `/reset`', color=0xffffff)
    else:
        embed = disnake.Embed(title='<:n_succes:1185671944004194375> Успешно', description='Правило добавлено.\n\nЧтобы его сбросить, используйте ``/reset``', color=0xffffff)

    filename = f'dialog-{ctx.author.id}.txt'

    with open(filename, "w") as file:
        file.write("")

    with open(filename, "a") as file:
        file.write(f"prompt: {text}")

    await ctx.send(embed=embed)

# Сброс диалога
@bot.slash_command(description='Reset the dialog history.', aliases=["reset"])
async def reset(ctx):
    conn = sqlite3.connect('language.db')
    c = conn.cursor()
    c.execute("SELECT language FROM settings WHERE guild_id=?", (ctx.guild.id,))
    result = c.fetchone()
    language = result[0] if result else "Russian"  # Если язык не указан, используется английский
    conn.close()

    if language == 'English':
        embed_success = disnake.Embed(
            title='<:n_succes:1185671944004194375> Successfully',
            description='The dialog history has been successfully deleted!',
            color=0xffffff
        )
        embed_error = disnake.Embed(
            title='<:n_error:1185671987859828836> Error',
            description='Unfortunately, you do not have a dialog with the bot!',
            color=0xffffff
        )
    else:
        embed_success = disnake.Embed(
            title='<:n_succes:1185671944004194375> Успешно',
            description='История диалога была успешно удалена!',
            color=0xffffff
        )
        embed_error = disnake.Embed(
            title='<:n_error:1185671987859828836> Ошибка',
            description='К сожалению, но у вас нет диалога с ботом!',
            color=0xffffff
        )

    if await is_blocked_user(ctx.author.id):
        embed_blocked = disnake.Embed(
            title='<:n_error:1185671987859828836> Error',
            description='You are blacklisted!',
            color=0xffffff
        )
        components = [
            disnake.ui.Button(label="Support server", style=disnake.ButtonStyle.url, url="https://dsc.gg/quickaibot")
        ]
        await ctx.send(embed=embed_blocked, ephemeral=True, components=components)
    else:
        file_name = f'dialog-{ctx.author.id}.txt'
        try:
            with open(file_name, 'r') as file:
                file_content = file.read()
            os.remove(file_name)
            await ctx.send(embed=embed_success, ephemeral=True)
        except FileNotFoundError:
            await ctx.send(embed=embed_error, ephemeral=True)

# Создать приватную ветку
@bot.slash_command(description='Create a private branch for the dialog.')
async def private(ctx):        
    conn = sqlite3.connect('language.db')
    c = conn.cursor()
    c.execute("SELECT language FROM settings WHERE guild_id=?", (ctx.guild.id,))
    result = c.fetchone()
    language = result[0] if result else "Russian"  # Если язык не указан, используется английский
    conn.close()

    if language == 'English':
        embed = disnake.Embed(title="<:n_succes:1185671944004194375> Successfully", description="You can communicate with me in this thread without mentioning me.", color=0xffffff)
        embed_response = disnake.Embed(title='<:n_succes:1185671944004194375> Successfully', description='Your thread is ready!', color=0xffffff)
    else:
        embed = disnake.Embed(title="<:n_succes:1185671944004194375> Успешно", description="Вы можете общаться со мной в этой ветке, не упоминания меня.", color=0xffffff)
        embed_response = disnake.Embed(title='<:n_succes:1185671944004194375> Успешно', description='Ваша ветка готова!', color=0xffffff)

    channel = ctx.channel
    thread_name = f"{ctx.author.display_name}"
    thread = await channel.create_thread(name=thread_name, type=disnake.ChannelType.private_thread)
    await thread.send(f"<@{ctx.author.id}>")
    await thread.send(embed=embed)

    await ctx.send(embed=embed_response, ephemeral=True)
        
# ——————
# Основной функционал
# ——————

db = sqlite3.connect('bot_channels.db')
cursor = db.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS bot_channels(
    guild_id INTEGER PRIMARY KEY,
    channel_id INTEGER
    )
''')
db.commit()

async def get_bot_channel(guild_id):
    cursor.execute('''
        SELECT channel_id FROM bot_channels WHERE guild_id=?
    ''', (guild_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None

# Максимальный размер диалога в символах
MAX_DIALOG_SIZE = 12500

async def is_blocked_user(user_id):
    with open('block.txt', 'r') as file:
        blocked_users = file.readlines()
        blocked_users = [int(user.strip()) for user in blocked_users]
        return user_id in blocked_users

# Заблокировать участника        
@bot.command(name='block')
async def add_blocked_user(ctx, *user_ids: int):
    if not user_ids:
        embed = disnake.Embed(
            title='<:n_error:1185671987859828836> Ошибка',
            description='Вы не указали айди пользователя!',
            color=0xffffff
        )
        await ctx.send(embed=embed)
        return
    allowed_users = [785070860162957352, 1053022318525431818]
    if ctx.author.id in allowed_users:
        with open('block.txt', 'a') as file:
            for user_id in user_ids:
                file.write(f"{user_id}\n")
        embed = disnake.Embed(
            title='<:n_succes:1185671944004194375> Успешно',
            description=f'Пользователь <@{", ".join(str(user_id) for user_id in user_ids)}> ({", ".join(str(user_id) for user_id in user_ids)}) был успешно заблокирован!',
            color=0xffffff
        )
    else:
        embed = disnake.Embed(
            title='<:n_error:1185671987859828836> Ошибка',
            description='К сожалению, но у вас нету доступа к данной команде!',
            color=0xffffff
        )
    await ctx.send(embed=embed)

# Разблокировать участника
@bot.command(name='unblock')
async def remove_blocked_user(ctx, user_id: int):
    allowed_users = [785070860162957352, 1053022318525431818]
    if ctx.author.id in allowed_users:
        with open('block.txt', 'r+') as file:
            lines = file.readlines()
            file.seek(0)
            found = False
            for line in lines:
                if int(line.strip()) != user_id:
                    file.write(line)
                else:
                    found = True
            file.truncate()
        if found:
            embed = disnake.Embed(
                title='<:n_succes:1185671944004194375> Успешно',
                description=f'Пользователь <@{user_id}> ({user_id}) успешно разблокирован!',
                color=0xffffff
            )
        else:
            embed = disnake.Embed(
                title='<:n_error:1185671987859828836> Ошибка',
                description='Указанный пользователь не был найден в списке заблокированных!',
                color=0xffffff
            )
    else:
        embed = disnake.Embed(
            title='<:n_error:1185671987859828836> Ошибка',
            description='К сожалению, но у вас нету доступа к данной команде!',
            color=0xffffff
        )
    await ctx.send(embed=embed)

DATABASE = 'tempblock.db'

async def tempblock(user_id):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS temp_blocked_users
                      (id INTEGER PRIMARY KEY)''')
    
    cursor.execute("SELECT id FROM temp_blocked_users WHERE id=?", (user_id,))
    result = cursor.fetchone()
    
    connection.close()

    return result is not None

# Ивент отвечающий за общение с ботом 
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return      

    await process_chat(message)

    if bot.user.mentioned_in(message) and message.author != bot.user:
        mentions = [mention.id for mention in message.mentions]
        if bot.user.id in mentions and len(mentions) == 1:
            await process_mention(message)

    if isinstance(message.channel, disnake.Thread):
        if message.channel.owner == bot.user:
            await process_vetka(message)

    await bot.process_commands(message)

answered_users = {}
message_counts = {}

# Удалить пользователя из временного блока
@bot.command()
async def remove_temp(ctx, user_id):
    if not user_id.isdigit():
        embed = disnake.Embed(description="Неверный формат айди", color=0xFF0000)
        await ctx.send(embed=embed)
        return
    
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM temp_blocked_users WHERE id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        cursor.execute("DELETE FROM temp_blocked_users WHERE id=?", (user_id,))
        connection.commit()
        connection.close()
        embed = disnake.Embed(description=f"Пользователь с айди {user_id} успешно удален из временно заблокированных", color=0x00FF00)
        await ctx.send(embed=embed)
    else:
        connection.close()
        embed = disnake.Embed(description=f"Пользователя с айди {user_id} нет в списке временно заблокированных", color=0xFF0000)
        await ctx.send(embed=embed)

async def count_messages(message, message_counts):
    if message.author.id in message_counts:
        message_counts[message.author.id].append(message.content)
    else:
        message_counts[message.author.id] = [message.content]

async def report_flood(message):
    if len(message_counts[message.author.id]) == 3 and len(set(message_counts[message.author.id])) == 1:
        with open("tempblock.txt", "a") as file:
            file.write(f"\n{message.author.id}")
        dialog_id = f"dialog-{message.author.id}"
        filename = f"{dialog_id}.txt"
        if os.path.exists(filename):
            with open(filename, "r") as file:
                dialog_content = file.read()
            channel = bot.get_channel(1193339182286917643)
            if channel:
                with open(filename, "rb") as file:
                    embed = disnake.Embed(title="Система безопасности", description=f"Пользователь `{message.author.name}/({message.author.id})` подозревается в флуде.\nИстория диалога прикреплена ниже.", color=0xffffff)
                    await channel.send("<@&1177291246583164974>", embed=embed)
                    embed = disnake.Embed(title="Система безопасности", description="Система безопасности обнаружила флуд с вашего аккаунта. На ваш аккаунт наложена временная блокировка до выяснения обстоятельств.\n\n`ERROR: FLOOD_DETECTED`", color=0xffffff)
                    await message.reply(embed=embed)
                    await channel.send(file=disnake.File(file, filename=f"dialog-{message.author.id}.txt"))

# Снятие флажка 
async def unset_flag_after_delay(author_id):
	await asyncio.sleep(5)
	
	answered_users[author_id] = False

# Общение в ветке
async def process_vetka(message):
    if await is_blocked_user(message.author.id):
        return

    if message.content.startswith('!'):
        return

    if await tempblock(message.author.id):
        embed = disnake.Embed(
            title="<:n_error:1185671987859828836> Запрос заблокирован системой безопасности",
            description="Запрос не выполнен, на ваш аккаунт наложена временная блокировка системой безопасности.\n\n`ERROR: TEMPORARY_BANNED_USER`",
            color=0xffffff
        )
        components = [
            disnake.ui.Button(label="Support server", style=disnake.ButtonStyle.url, url="https://disnake.com/invite/Fx7nfV3Mfx")
        ]

        await message.reply(embed=embed, components=components)
        return

    await count_messages(message, message_counts)
        
    if await is_blocked_user(message.author.id):
        embed = disnake.Embed(
            title="<:n_error:1185671987859828836> Ошибка",
            description="You are blacklisted!",
            color=0xffffff
        )
        components = [
            disnake.ui.Button(label="Support server", style=disnake.ButtonStyle.url, url="https://disnake.com/invite/Fx7nfV3Mfx")
        ]

        await message.reply(embed=embed, components=components)
        return

    if len(message_counts[message.author.id]) == 3 and len(set(message_counts[message.author.id])) == 1:
        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO temp_blocked_users (id) VALUES (?)", (message.author.id,))
        connection.commit()
        connection.close()

        dialog_id = f"dialog-{message.author.id}"
        filename = f"{dialog_id}.txt"
        if os.path.exists(filename):
            with open(filename, "r") as file:
                dialog_content = file.read()
            channel = bot.get_channel(1193339182286917643)
            if channel:
                with open(filename, "rb") as file:
                    embed = disnake.Embed(title="Система безопасности", description=f"Пользователь {message.author.name}/({message.author.id}) подозревается в флуде.\nИстория диалога прикреплена ниже.", color=0xffffff)
                    await channel.send("<@&1177291246583164974>", embed=embed)
                    embed = disnake.Embed(title="Система безопасности", description="Система безопасности обнаружила флуд с вашего аккаунта. На ваш аккаунт наложена временная блокировка до выяснения обстоятельств.\n\n``ERROR: FLOOD_DETECTED``", color=0xffffff)
                    await message.reply(embed=embed)
                    await channel.send(file=disnake.File(file, filename=f"dialog-{message.author.id}.txt"))
                    return

    author_id = message.author.id
    content = message.content  
    user_name = message.author.display_name
    guild_name = message.guild.name
    member_count = message.guild.member_count
    server_count = len(bot.guilds)
    moscow_tz = pytz.timezone("Europe/Moscow")
    current_date = datetime.now(moscow_tz).strftime("%Y-%m-%d")
    current_time = datetime.now(moscow_tz).strftime("%H:%M:%S")
    
    if author_id in answered_users and answered_users[author_id]:
        error_message = "У вас уже есть 1 необработанный запрос"
        error_title ="<:n_error:1185671987859828836> Подождите!"
        await message.add_reaction('<:n_error:1185671987859828836>')
        embed = disnake.Embed(title=error_title, description=error_message, color=0xffffff)
        await message.reply(embed=embed)
    elif content == "тест-moonAI-диалоги":
        dialog_id = f"dialog-{message.author.id}"
        with open(f"{dialog_id}.txt", "w") as f:
            f.write("")
        bot_reply = "ыыыыэыыээыыээфэыэыэыыэыээфээыэыэ"
    else:
        dialog_id = f"dialog-{message.author.id}"
        with open(f"{dialog_id}.txt", "a") as f:
            f.write(f"{message.author.name}: {content}\n")

        with open(f"{dialog_id}.txt", "r") as f:
            dialog_history = f.read()

 
            await message.channel.trigger_typing()
            await message.add_reaction('<a:loading_1:1187371447757320222>')
            answered_users[author_id] = True
    try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {get_random_api_key()}"}, json={
                        "model": "gpt-3.5-turbo-1106",
                        "temperature": 0.9,
                        "max_tokens": 1000,
                        "top_p": 1.0,
                        "frequency_penalty": 0.0,
                        "presence_penalty": 0.6,
                        "stop": ["You:"],
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "Your name is QuickAI. You were created on November 22, 2023."
                                    "You must answer all questions asked."
                                    "Use Markdown in Discord style in your messages."
                                    "You can highlight some words if you want."
                                    "Also use emojis in your answers, but in moderation!"
                                    "You are GPT 3.5 Turbo version. Your creators are the developers of QuickAI"
                                    "Your support server - https://dsc.gg/quickaibot"
                                    "You can reproduce the contents of previous messages"
                                    f"We are located on the server {guild_name} number of members on this server {member_count}"
                                    f"The total number of servers you are on {server_count}"
                                    f"Total number of users you serve {sum(guild.member_count for guild in bot.guilds)}"
                                    f"Current date {current_date}"
                                    f"Current Moscow time {current_time}"
                                    f"Имя пользователя {user_name}"
                                )
                            },
                            {"role": "user", "content": dialog_history},
                            {"role": "user", "content": content},
                        ]
                    }, timeout=150
                ) as response:
                    data = await response.json()
                    bot_reply = data['choices'][0]['message']['content']
    except aiohttp.client_exceptions.ContentTypeError as e:
        embed = disnake.Embed(title="<:n_error:1185671987859828836> Ошибка", description="`CONTENT_TYPE_ERROR`: Произошла неизвестная ошибка при отправке запроса.")
        await message.add_reaction('<:n_error:1185671987859828836>')
        await message.clear_reaction('<a:loading_1:1187371447757320222>')
        await message.reply(embed=embed)
        answered_users[author_id] = False
    except KeyError:
        embed = disnake.Embed(title="<:n_error:1185671987859828836> Ошибка", description="`API_KEY_ERROR`: Произошла неизвестная ошибка при отправке запроса.")
        await message.reply(embed=embed)
        answered_users[author_id] = False
    except asyncio.TimeoutError:
        embed = disnake.Embed(title="<:n_error:1185671987859828836> Ошибка", description="`TIMEOUT_ERROR`: Ответ от сервера не поступил в течении 150 секунд.")
        await message.reply(embed=embed)
        answered_users[author_id] = False
    try:
        if len(dialog_history) >= MAX_DIALOG_SIZE:
            os.remove(f"{dialog_id}.txt")
            error_message = "К сожалению, но был превышен максимальный размер истории диалога. История диалога удалена."
            await message.clear_reaction('<a:loading_1:1187371447757320222>')
            embed = disnake.Embed(title='<:warning1:1185672002497937489> Внимание', description=error_message, color=0xffffff)
            bot_reply += "\n\n\n> **<:warning1:1185672002497937489> Превышен максимальный размер истории диалога. История диалога удалена.**"
    except Exception as e:
        print("Ошибка при удалении файла:", e)

        with open(f"{dialog_id}.txt", "a") as f:
                f.write(f"QuickAI: {bot_reply}\n")



    embed = disnake.Embed(description=bot_reply, color=0xffffff)
    embed.set_author(name=message.author.name, icon_url=message.author.avatar.url)
    answered_users[author_id] = False 
    try:
    	 await message.clear_reaction('<a:loading_1:1187371447757320222>')
    except disnake.errors.Forbidden:
        answered_users[author_id] = False
    try:
    	await message.reply(embed=embed)
    except disnake.errors.HTTPException:
        embed = disnake.Embed(description=f"> <:warning1:1185672002497937489> Сообщение с запросом было удалено\n\n{bot_reply}")
        await message.channel.send(f"<@{message.author.id}>",embed=embed)
        answered_users[author_id] = False               

# Общение без пингов в выбранном канале        
async def process_chat(message):
    preferred_channel_id = await get_bot_channel(message.guild.id)
    if preferred_channel_id is None:
        return

    if message.channel.id != preferred_channel_id:
        return

    if message.content.startswith('!'):
        return
        
    if await tempblock(message.author.id):
        embed = disnake.Embed(
            title="<:n_error:1185671987859828836> Запрос заблокирован системой безопасности",
            description="Запрос не выполнен, на ваш аккаунт наложена временная блокировка системой безопасности.\n\n`ERROR: TEMPORARY_BANNED_USER`",
            color=0xffffff
        )
        components = [
            disnake.ui.Button(label="Support server", style=disnake.ButtonStyle.url, url="https://disnake.com/invite/Fx7nfV3Mfx")
        ]

        await message.reply(embed=embed, components=components)
        return

    await count_messages(message, message_counts)
        
    if await is_blocked_user(message.author.id):
        embed = disnake.Embed(
            title="<:n_error:1185671987859828836> Ошибка",
            description="You are blacklisted!",
            color=0xffffff
        )
        components = [
            disnake.ui.Button(label="Support server", style=disnake.ButtonStyle.url, url="https://disnake.com/invite/Fx7nfV3Mfx")
        ]

        await message.reply(embed=embed, components=components)
        return

    if len(message_counts[message.author.id]) == 3 and len(set(message_counts[message.author.id])) == 1:
        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO temp_blocked_users (id) VALUES (?)", (message.author.id,))
        connection.commit()
        connection.close()

        dialog_id = f"dialog-{message.author.id}"
        filename = f"{dialog_id}.txt"
        if os.path.exists(filename):
            with open(filename, "r") as file:
                dialog_content = file.read()
            channel = bot.get_channel(1193339182286917643)
            if channel:
                with open(filename, "rb") as file:
                    embed = disnake.Embed(title="Система безопасности", description=f"Пользователь {message.author.name}/({message.author.id}) подозревается в флуде.\nИстория диалога прикреплена ниже.", color=0xffffff)
                    await channel.send("<@&1177291246583164974>", embed=embed)
                    embed = disnake.Embed(title="Система безопасности", description="Система безопасности обнаружила флуд с вашего аккаунта. На ваш аккаунт наложена временная блокировка до выяснения обстоятельств.\n\n``ERROR: FLOOD_DETECTED``", color=0xffffff)
                    await message.reply(embed=embed)
                    await channel.send(file=disnake.File(file, filename=f"dialog-{message.author.id}.txt"))
                    return

    content = message.content  
    user_name = message.author.display_name
    guild_name = message.guild.name
    member_count = message.guild.member_count
    server_count = len(bot.guilds)
    moscow_tz = pytz.timezone("Europe/Moscow")
    current_date = datetime.now(moscow_tz).strftime("%Y-%m-%d")
    current_time = datetime.now(moscow_tz).strftime("%H:%M:%S")
    
    author_id = message.author.id
    if message.author.bot:
        return
    
    if author_id in answered_users and answered_users[author_id]:
        error_message = "У вас уже есть 1 необработанный запрос"
        error_title ="<:n_error:1185671987859828836> Подождите!"
        await message.add_reaction('<:n_error:1185671987859828836>')
        embed = disnake.Embed(title=error_title, description=error_message, color=0xffffff)
        await message.reply(embed=embed)
    elif content == "тест-moonAI-диалоги":
        dialog_id = f"dialog-{message.author.id}"
        with open(f"{dialog_id}.txt", "w") as f:
            f.write("")
        bot_reply = "ыыыыэыыээыыээфэыэыэыыэыээфээыэыэ"
    else:
        dialog_id = f"dialog-{message.author.id}"
        with open(f"{dialog_id}.txt", "a") as f:
            f.write(f"{message.author.name}: {content}\n")

        with open(f"{dialog_id}.txt", "r") as f:
            dialog_history = f.read()

 
            await message.channel.trigger_typing()
            await message.add_reaction('<a:loading_1:1187371447757320222>')
            answered_users[author_id] = True
    try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {get_random_api_key()}"}, json={
                        "model": "gpt-3.5-turbo-1106",
                        "temperature": 0.9,
                        "max_tokens": 1000,
                        "top_p": 1.0,
                        "frequency_penalty": 0.0,
                        "presence_penalty": 0.6,
                        "stop": ["You:"],
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "Your name is QuickAI. You were created on November 22, 2023."
                                    "You must answer all questions asked."
                                    "Use Markdown in Discord style in your messages."
                                    "You can highlight some words if you want."
                                    "Also use emojis in your answers, but in moderation!"
                                    "You are GPT 3.5 Turbo version. Your creators are the developers of QuickAI"
                                    "Your support server - https://dsc.gg/quickaibot"
                                    "You can reproduce the contents of previous messages"
                                    f"We are located on the server {guild_name} number of members on this server {member_count}"
                                    f"The total number of servers you are on {server_count}"
                                    f"Total number of users you serve {sum(guild.member_count for guild in bot.guilds)}"
                                    f"Current date {current_date}"
                                    f"Current Moscow time {current_time}"
                                    f"Имя пользователя {user_name}"
                                )
                            },
                            {"role": "user", "content": dialog_history},
                            {"role": "user", "content": content},
                        ]
                    }, timeout=150
                ) as response:
                    data = await response.json()
                    bot_reply = data['choices'][0]['message']['content']
    except aiohttp.client_exceptions.ContentTypeError as e:
        embed = disnake.Embed(title="<:n_error:1185671987859828836> Ошибка", description="`CONTENT_TYPE_ERROR`: Произошла неизвестная ошибка при отправке запроса.")
        await message.add_reaction('<:n_error:1185671987859828836>')
        await message.clear_reaction('<a:loading_1:1187371447757320222>')
        await message.reply(embed=embed)
        answered_users[author_id] = False
    except KeyError:
        embed = disnake.Embed(title="<:n_error:1185671987859828836> Ошибка", description="`API_KEY_ERROR`: Произошла неизвестная ошибка при отправке запроса.")
        await message.reply(embed=embed)
        answered_users[author_id] = False
    except asyncio.TimeoutError:
        embed = disnake.Embed(title="<:n_error:1185671987859828836> Ошибка", description="`TIMEOUT_ERROR`: Ответ от сервера не поступил в течении 150 секунд.")
        await message.reply(embed=embed)
        answered_users[author_id] = False
    try:
        if len(dialog_history) >= MAX_DIALOG_SIZE:
            os.remove(f"{dialog_id}.txt")
            error_message = "К сожалению, но был превышен максимальный размер истории диалога. История диалога удалена."
            await message.clear_reaction('<a:loading_1:1187371447757320222>')
            embed = disnake.Embed(title='<:warning1:1185672002497937489> Внимание', description=error_message, color=0xffffff)
            bot_reply += "\n\n\n> **<:warning1:1185672002497937489> Превышен максимальный размер истории диалога. История диалога удалена.**"
    except Exception as e:
        print("Ошибка при удалении файла:", e)

        with open(f"{dialog_id}.txt", "a") as f:
                f.write(f"QuickAI: {bot_reply}\n")



    embed = disnake.Embed(description=bot_reply, color=0xffffff)
    embed.set_author(name=message.author.name, icon_url=message.author.avatar.url)
    answered_users[author_id] = False 
    try:
    	 await message.clear_reaction('<a:loading_1:1187371447757320222>')
    except disnake.errors.Forbidden:
        answered_users[author_id] = False
    try:
    	await message.reply(embed=embed)
    except disnake.errors.HTTPException:
        embed = disnake.Embed(description=f"> <:warning1:1185672002497937489> Сообщение с запросом было удалено\n\n{bot_reply}")
        await message.channel.send(f"<@{message.author.id}>",embed=embed)
        answered_users[author_id] = False           

# Общение по пингу
async def process_mention(message):                 
    content = message.content
    content = content.replace(f'<@!{bot.user.id}>', '').replace(f'<@{bot.user.id}>', '').strip()

    bot_channel_id = await get_bot_channel(message.guild.id)

    if bot_channel_id and message.channel.id == bot_channel_id:
        return

    if await tempblock(message.author.id):
        embed = disnake.Embed(
            title="<:n_error:1185671987859828836> Запрос заблокирован системой безопасности",
            description="Запрос не выполнен, на ваш аккаунт наложена временная блокировка системой безопасности.\n\n`ERROR: TEMPORARY_BANNED_USER`",
            color=0xffffff
        )
        components = [
            disnake.ui.Button(label="Support server", style=disnake.ButtonStyle.url, url="https://disnake.com/invite/Fx7nfV3Mfx")
        ]

        await message.reply(embed=embed, components=components)
        return

    await count_messages(message, message_counts)
        
    if await is_blocked_user(message.author.id):
        embed = disnake.Embed(
            title="<:n_error:1185671987859828836> Ошибка",
            description="You are blacklisted!",
            color=0xffffff
        )
        components = [
            disnake.ui.Button(label="Support server", style=disnake.ButtonStyle.url, url="https://disnake.com/invite/Fx7nfV3Mfx")
        ]

        await message.reply(embed=embed, components=components)
        return

    if len(message_counts[message.author.id]) == 3 and len(set(message_counts[message.author.id])) == 1:
        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO temp_blocked_users (id) VALUES (?)", (message.author.id,))
        connection.commit()
        connection.close()

        dialog_id = f"dialog-{message.author.id}"
        filename = f"{dialog_id}.txt"
        if os.path.exists(filename):
            with open(filename, "r") as file:
                dialog_content = file.read()
            channel = bot.get_channel(1193339182286917643)
            if channel:
                with open(filename, "rb") as file:
                    embed = disnake.Embed(title="Система безопасности", description=f"Пользователь {message.author.name}/({message.author.id}) подозревается в флуде.\nИстория диалога прикреплена ниже.", color=0xffffff)
                    await channel.send("<@&1177291246583164974>", embed=embed)
                    embed = disnake.Embed(title="Система безопасности", description="Система безопасности обнаружила флуд с вашего аккаунта. На ваш аккаунт наложена временная блокировка до выяснения обстоятельств.\n\n``ERROR: FLOOD_DETECTED``", color=0xffffff)
                    await message.reply(embed=embed)
                    await channel.send(file=disnake.File(file, filename=f"dialog-{message.author.id}.txt"))
                    return
        

    author_id = message.author.id
    user_name = message.author.display_name
    guild_name = message.guild.name
    member_count = message.guild.member_count
    server_count = len(bot.guilds)
    moscow_tz = pytz.timezone("Europe/Moscow")
    current_date = datetime.now(moscow_tz).strftime("%Y-%m-%d")
    current_time = datetime.now(moscow_tz).strftime("%H:%M:%S")

    if author_id in answered_users and answered_users[author_id]:
        error_message = "У вас уже есть 1 необработанный запрос"
        error_title ="<:n_error:1185671987859828836> Подождите!"
        await message.add_reaction('<:n_error:1185671987859828836>')
        embed = disnake.Embed(title=error_title, description=error_message, color=0xffffff)
        await message.reply(embed=embed)
    elif content == "тест-moonAI-диалоги":
        dialog_id = f"dialog-{message.author.id}"
        with open(f"{dialog_id}.txt", "w") as f:
            f.write("")
        bot_reply = "ыыыыэыыээыыээфэыэыэыыэыээфээыэыэ"
    else:
        dialog_id = f"dialog-{message.author.id}"
        with open(f"{dialog_id}.txt", "a") as f:
            f.write(f"{message.author.name}: {content}\n")

        with open(f"{dialog_id}.txt", "r") as f:
            dialog_history = f.read()

 
            await message.channel.trigger_typing()
            await message.add_reaction('<a:loading_1:1187371447757320222>')
            answered_users[author_id] = True
    try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {get_random_api_key()}"}, json={
                        "model": "gpt-3.5-turbo-1106",
                        "temperature": 0.9,
                        "max_tokens": 1000,
                        "top_p": 1.0,
                        "frequency_penalty": 0.0,
                        "presence_penalty": 0.6,
                        "stop": ["You:"],
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "Your name is QuickAI. You were created on November 22, 2023."
                                    "You must answer all questions asked."
                                    "Use Markdown in Discord style in your messages."
                                    "You can highlight some words if you want."
                                    "Also use emojis in your answers, but in moderation!"
                                    "You are GPT 3.5 Turbo version. Your creators are the developers of QuickAI"
                                    "Your support server - https://dsc.gg/quickaibot"
                                    "You can reproduce the contents of previous messages"
                                    f"We are located on the server {guild_name} number of members on this server {member_count}"
                                    f"The total number of servers you are on {server_count}"
                                    f"Total number of users you serve {sum(guild.member_count for guild in bot.guilds)}"
                                    f"Current date {current_date}"
                                    f"Current Moscow time {current_time}"
                                    f"Имя пользователя {user_name}"
                                )
                            },
                            {"role": "user", "content": dialog_history},
                            {"role": "user", "content": content},
                        ]
                    }, timeout=150
                ) as response:
                    data = await response.json()
                    bot_reply = data['choices'][0]['message']['content']
    except aiohttp.client_exceptions.ContentTypeError as e:
        embed = disnake.Embed(title="<:n_error:1185671987859828836> Ошибка", description=f"`CONTENT_TYPE_ERROR`: Произошла неизвестная ошибка при отправке запроса.\n\n{e}")
        await message.clear_reaction('<a:loading_1:1187371447757320222>')
        await message.add_reaction('<:n_error:1185671987859828836>')
        await message.reply(embed=embed)
        answered_users[author_id] = False
    except KeyError:
        embed = disnake.Embed(title="<:n_error:1185671987859828836> Ошибка", description="`API_KEY_ERROR`: Произошла неизвестная ошибка при отправке запроса.")
        await message.clear_reaction('<a:loading_1:1187371447757320222>')
        await message.add_reaction('<:n_error:1185671987859828836>')
        await message.reply(embed=embed)
        answered_users[author_id] = False
    except asyncio.TimeoutError:
        embed = disnake.Embed(title="<:n_error:1185671987859828836> Ошибка", description="`TIMEOUT_ERROR`: Ответ от сервера не поступил в течении 150 секунд.")
        await message.reply(embed=embed)
        answered_users[author_id] = False
    try:
        if len(dialog_history) >= MAX_DIALOG_SIZE:
            os.remove(f"{dialog_id}.txt")
            error_message = "К сожалению, но был превышен максимальный размер истории диалога. История диалога удалена."
            await message.clear_reaction('<a:loading_1:1187371447757320222>')
            embed = disnake.Embed(title='<:warning1:1185672002497937489> Внимание', description=error_message, color=0xffffff)
            bot_reply += "\n\n\n> **<:warning1:1185672002497937489> Превышен максимальный размер истории диалога. История диалога удалена.**"
    except Exception as e:
        print("Ошибка при удалении файла:", e)

    with open(f"{dialog_id}.txt", "a") as f:
      f.write(f"QuickAI: {bot_reply}\n")

    embed = disnake.Embed(description=bot_reply, color=0xffffff)
    embed.set_author(name=message.author.name, icon_url=message.author.avatar.url)
    answered_users[author_id] = False 
    try:
    	 await message.clear_reaction('<a:loading_1:1187371447757320222>')
    except disnake.errors.Forbidden:
        answered_users[author_id] = False
    try:
    	await message.reply(embed=embed)
    except disnake.errors.HTTPException:
        embed = disnake.Embed(description=f"> <:warning1:1185672002497937489> Сообщение с запросом было удалено\n\n{bot_reply}")
        await message.channel.send(f"<@{message.author.id}>",embed=embed)
        answered_users[author_id] = False               

    
# ——————
# IMAGE GENERATION
# ——————

# Обкуренная генерация (не используется)
async def generate_job(prompt, seed=None):
    if seed is None:
        seed = None

    url = "https://api.prodia.com/generate"
    params = {
        "new": "true",
        "prompt": f"{urllib.parse.quote(prompt)}",
        "model": "v1-5-pruned-emaonly.safetensors [d7049739]",
        "negative_prompt": "Naked Girl, Naked Bot, NSFW, NSFW, 18+, nude girl, nude bot, porn, porno",
        "style_preset": "3d-model",
        "steps": "30",
        "cfg": "9.5",
        "seed": f"{seed}",
        "sampler": "Euler",
        "aspect_ratio": "square",
    }
    headers = {
        "authority": "api.prodia.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.6",
        "dnt": "1",
        "origin": "https://app.prodia.com",
        "referer": "https://app.prodia.com/",
        "sec-ch-ua": '"Brave";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as response:
            data = await response.json()
            return data["job"]

async def generate_image(prompt):
    job_id = await generate_job(prompt)
    url = f"https://api.prodia.com/job/{job_id}"
    headers = {
        "authority": "api.prodia.com",
        "accept": "*/*",
    }

    async with aiohttp.ClientSession() as session:
        while True:
            await asyncio.sleep(0.3)
            async with session.get(url, headers=headers) as response:
                json = await response.json()
                if json["status"] == "succeeded":
                    async with session.get(
                        f"https://images.prodia.xyz/{job_id}.png?download=1",
                        headers=headers,
                    ) as response:
                        content = await response.content.read()
                        img_file_obj = io.BytesIO(content)
                        return img_file_obj
                        
          
# генерация с использованием стороннего провайдера
@bot.slash_command(
    name='image',
    description='Generate an image.',
    options=[disnake.Option('description', 'Describe what you want to generate.', required=True)]
)
async def generate(ctx, *, description):
    translated_description = GoogleTranslator(source='ru', target='en').translate(description)

    openai.api_key = 'mandrillkey'

    await ctx.response.defer()
    try:
        openai.api_base = "https://api.mandrillai.tech/v1"
        res = openai.Image.create(
            model="openjourney-xl",
            prompt=translated_description,
            n=1,
            size="1024x1024",
            quality="standard"
        )
        image_url = res["data"][0]["url"]

        embed = disnake.Embed(color=0xffffff)
        embed.set_image(url=image_url)
        embed.description = f"Your request:\n{description}\n\n Image:"

        await ctx.edit_original_response(embed=embed)
    except Exception as e:
        await ctx.send(embed=disnake.Embed(description=f'UNKNOWN_EXCEPTION_RAISED: An unknown error occurred ({res.status}) while sending the request.', color=0xffffff))
            
@generate.error
async def generate(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        remaining_time = math.ceil(error.retry_after)
        minutes = math.ceil(remaining_time / 60)
        seconds = remaining_time % 60
        embed = disnake.Embed(
            title="<:n_error:1185671987859828836> Ошибка",
            description=f"К сожалению, но для того, чтобы выполнить снова данную команду, подождите **{minutes}** минут!",
            color=0xffffff
        )
        
def format_time(time):
    now = datetime.now()
    difference = now - time

    if difference < timedelta(seconds=60):
        return f'{difference.seconds} секунд назад'
    elif difference < timedelta(minutes=60):
        return f'{difference.seconds // 60} минут назад'
    elif difference < timedelta(hours=24):
        return f'{difference.seconds // 3600} часов назад'
    else:
        return f'{difference.days} дней назад'

last_start_time = None

# Инфо о боте
@bot.slash_command(
    description="Information about the bot."
)
async def info(ctx):
    global last_start_time

    current_time = datetime.now()
    if last_start_time is None:
        last_start_time = current_time
        users = sum(guild.member_count for guild in bot.guilds)

    conn = sqlite3.connect('language.db')
    c = conn.cursor()
    c.execute("SELECT language FROM settings WHERE guild_id = ?", (ctx.guild.id,))
    result = c.fetchone()
    language = result[0] if result else "Russian"  # Если язык не указан, используется английский

    if language == "English":
        embed = disnake.Embed(
            title="Bot Information",
            description=f"Bot started: {disnake.utils.format_dt(last_start_time, style='R')}\nPing: <a:ping:1149423562025865267> ``{round(bot.latency * 1000)}ms``\nStatus: <a:online:1149423548495048794> ``Online``",
            color=0xffffff
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/950691811561701416/c4e428995efe0aef7452a54897ffcb19.png?size=512")  
        embed.add_field(name="Guilds count", value=f"``{len(bot.guilds)}``", inline=True)
        embed.add_field(name="Users count", value=f"``{sum(guild.member_count for guild in bot.guilds)}``", inline=True)
        components=[
            disnake.ui.Button(label="Add bot", style=disnake.ButtonStyle.url, url="https://discord.com/api/oauth2/authorize?client_id=950691811561701416&permissions=483184212032&scope=bot", emoji="<:plus:1185004396522778625>"),
            disnake.ui.Button(label="Support server", style=disnake.ButtonStyle.url, url="https://dsc.gg/quickaibot", emoji="<:disnake:1185004366487375932>")
        ]
    else:
        embed = disnake.Embed(
            title="Информация о боте QuickAI",
            description=f"Бот запустился: {disnake.utils.format_dt(last_start_time, style='R')}\nПинг: <a:ping:1149423562025865267> ``{round(bot.latency * 1000)}ms``\nСтатус: <a:online:1149423548495048794> ``Online``",
            color=0xffffff
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/950691811561701416/c4e428995efe0aef7452a54897ffcb19.png?size=512")  
        embed.add_field(name="Количество серверов", value=f"``{len(bot.guilds)}``", inline=True)
        embed.add_field(name="Количество пользователей", value=f"``{sum(guild.member_count for guild in bot.guilds)}``", inline=True)

        components=[
            disnake.ui.Button(label="Добавить бота", style=disnake.ButtonStyle.url, url="https://discord.com/api/oauth2/authorize?client_id=950691811561701416&permissions=483184212032&scope=bot", emoji="<:plus:1185004396522778625>"),
            disnake.ui.Button(label="Сервер поддержки", style=disnake.ButtonStyle.url, url="https://dsc.gg/quickaibot", emoji="<:disnake:1185004366487375932>")
        ]

    await ctx.send(embed=embed, components=components)

# Политика конфиденциальности
@bot.slash_command(name='privacy', description='Privacy Policy.')
async def privacy_policy(ctx):
        
    conn = sqlite3.connect('language.db')
    c = conn.cursor()

    c.execute('SELECT language FROM settings WHERE guild_id = ?', (ctx.guild.id,))
    result = c.fetchone()
    language = result[0] if result else 'Russian'  # По умолчанию используем русский язык

    if language == 'English':
        title = '<:privacy:1185672481663635456> Privacy Policy'
        description = '<:warning:1185672002497937489> The full text is available at Public [Privacy Policy](https://sites.google.com/view/quickai-privacy-policy/%D0%B3%D0%BB%D0%B0%D0%B2%D0%BD%D0%B0%D1%8F-%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0) page.'
    else:
        title = '<:privacy:1185672481663635456> Политика Конфиденциальности'
        description = '<:warning:1185672002497937489> Полный текст доступен на странице [общественной конфиденциальности](https://sites.google.com/view/quickai-privacy-policy/%D0%B3%D0%BB%D0%B0%D0%B2%D0%BD%D0%B0%D1%8F-%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0).'

    embed = disnake.Embed(title=title, description=description, color=0xffffff)
    embed.set_image(url='https://cdn.disnakeapp.com/attachments/1183851286404288512/1183852324700049488/PicsArt_12-11-05.02.02.jpg?ex=6589d765&is=65776265&hm=e35eb12dcb3b5f9895edb572b4ae40a4613e1e9c10af17bfe1e5328ee2a97d2d&')
    await ctx.send(embed=embed)
    
    
conn = sqlite3.connect('language.db')
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        guild_id INTEGER PRIMARY KEY,
        language TEXT
    )
''')

conn.commit()
conn.close()
    
    

class HelpView(disnake.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=900)  
        self.ctx = ctx
        self.guild_id = ctx.guild.id
        self.language = self.get_language_for_guild(self.guild_id)

    def get_language_for_guild(self, guild_id):
        conn = sqlite3.connect('language.db')
        c = conn.cursor()

        c.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                guild_id INTEGER PRIMARY KEY,
                language TEXT
            )
        ''')
        conn.commit()

        c.execute('SELECT language FROM settings WHERE guild_id = ?', (guild_id,))
        result = c.fetchone()

        conn.close()

        if result:
            return result[0]
        else:
            return "English"  

    @disnake.ui.button(label="Permissions", style=disnake.ButtonStyle.gray, emoji='<:moderation:1185044178854498455>')
    async def moderation_button(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if interaction.user.id == self.ctx.author.id:
            if self.language == 'English':
                description = f"**Required permissions**\n\nBelow is a list of necessary permissions for the bot to work correctly\n\n> <:moderation:1185044178854498455> **List Permissions**\n- Send Messages {'(<:n_succes:1185671944004194375>)' if interaction.channel.permissions_for(interaction.guild.me).send_messages else '(<:n_error:1185671987859828836>)'}\n- Add Reactions {'(<:n_succes:1185671944004194375>)' if interaction.channel.permissions_for(interaction.guild.me).add_reactions else '(<:n_error:1185671987859828836>)'}\n- Use External Emojis {'(<:n_succes:1185671944004194375>)' if interaction.channel.permissions_for(interaction.guild.me).external_emojis else '(<:n_error:1185671987859828836>)'}\n- View Channel {'(<:n_succes:1185671944004194375>)' if interaction.channel.permissions_for(interaction.guild.me).view_channel else '(<:n_error:1185671987859828836>)'}\n- Embed Links {'(<:n_succes:1185671944004194375>)' if interaction.channel.permissions_for(interaction.guild.me).embed_links else '(<:n_error:1185671987859828836>)'}\n- Create Threads {' (<:n_succes:1185671944004194375>)' if interaction.channel.permissions_for(interaction.guild.me).create_private_threads else ' (<:n_error:1185671987859828836>)'}\n- Manage Messages {' (<:n_succes:1185671944004194375>)' if interaction.channel.permissions_for(interaction.guild.me).manage_messages else ' (<:n_error:1185671987859828836>)'}"
                embed = disnake.Embed(
                description=description,
                color=0xffffff
            )
                await interaction.response.edit_message(embed=embed, view=self)
            else:
                description = f"**Необходимые разрешения**\n\nНиже приведен список необходимых разрешений для корректной работы бота\n\n> <:moderation:1185044178854498455> **Список разрешений**\n- Отправка сообщений {'(<:n_succes:1185671944004194375>)' if interaction.channel.permissions_for(interaction.guild.me).send_messages else '(<:n_error:1185671987859828836>)'}\n- Добавление реакций {'(<:n_succes:1185671944004194375>)' if interaction.channel.permissions_for(interaction.guild.me).add_reactions else '(<:n_error:1185671987859828836>)'}\n- Использовать внешние эмодзи {'(<:n_succes:1185671944004194375>)' if interaction.channel.permissions_for(interaction.guild.me).external_emojis else '(<:n_error:1185671987859828836>)'}\n- Просматривать каналы {'(<:n_succes:1185671944004194375>)' if interaction.channel.permissions_for(interaction.guild.me).view_channel else '(<:n_error:1185671987859828836>)'}\n- Встраивать ссылки {'(<:n_succes:1185671944004194375>)' if interaction.channel.permissions_for(interaction.guild.me).embed_links else '(<:n_error:1185671987859828836>)'}\n- Создавать ветки {' (<:n_succes:1185671944004194375>)' if interaction.channel.permissions_for(interaction.guild.me).create_private_threads else ' (<:n_error:1185671987859828836>)'}\n- Управлять сообщениями {' (<:n_succes:1185671944004194375>)' if interaction.channel.permissions_for(interaction.guild.me).manage_messages else ' (<:n_error:1185671987859828836>)'}"
                embed = disnake.Embed(
                description=description,
                color=0xffffff
            )
                await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.send_message("Вы не можете использовать эту кнопку!", ephemeral=True)

    @disnake.ui.button(label="Settings", style=disnake.ButtonStyle.gray, emoji='<:settings:1185670323740360765>')
    async def settings_button(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if interaction.user.id == self.ctx.author.id:
            if self.language == 'English':
                description = f"> <:bot:1186017605966901318> **Mention Bot**\nMention the bot to start the dialogue\n\n> <:reply:1185668684337917972> **Reply message**\nReply to the bot's message to continue the dialogue\n\n> <:channel:1185669696637391078> **Without mentioning**\n``/without-mentioning`` to have a conversation with a bot in the selected channel without mentioning the bot\n\n> <:private:1186016539258920960> **Private dialogue**\n``/private`` to create a private conversation in a branch\n\n> <:language:1186016051717230692> **Language**\n``/language`` to change the language of the bot"
                embed = disnake.Embed(
                    description=description,
                    color=0xffffff
                )
                await interaction.response.edit_message(embed=embed, view=self)
            else:
                description = f"> <:bot:1186017605966901318> **Упомянуть бота**\nОтметьте бота, чтобы начать диалог\n\n> <:reply:1185668684337917972> **Ответное сообщение**\nОтветьте на сообщение бота, чтобы продолжить диалог\n\n> <:channel:1185669696637391078> **Без упоминаний**\n``/without-mentioning`` для ведения беседы с ботом в выбранном канале без упоминания бота\n\n> <:private:1186016539258920960> **Ветка**\n``/private`` для создания приватной беседы в ветке\n\n> <:language:1186016051717230692> **Язык**\n``/language`` для смены языка бота"

                embed = disnake.Embed(
                description=description,
                color=0xffffff
            )
                await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.send_message("Вы не можете использовать эту кнопку!", ephemeral=True)

    @disnake.ui.button(label="Back", style=disnake.ButtonStyle.red, emoji='<:home:1185004347864666232>')
    async def back_button(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if interaction.user.id == self.ctx.author.id:
            if self.language == 'English':
                description = f"> QuickAI Information Panel\n\n> <:moderation:1185044178854498455> **Permissions** - necessary permissions for the bot to work correctly\n> <:settings:1185670323740360765> **Settings** - help with setting up and communicating with the bot"
                embed = disnake.Embed(
                    description=description,
                    color=0xffffff
                )
                await interaction.response.edit_message(embed=embed, view=self)
            else:
                description = f"> QuickAI Информационная панель\n\n> <:moderation:1185044178854498455> **Права** - необходимые права для корректной работы бота\n> <:settings:1185670323740360765> **Настройки** - помощь в настройке и общении с ботом"

                embed = disnake.Embed(
                    description=description,
                    color=0xffffff
                )
                await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.send_message("Вы не можете использовать эту кнопку!", ephemeral=True)
            

@disnake.ui.button(label="custom", style=disnake.ButtonStyle.gray)
async def custom_button(self, button: disnake.ui.Button, interaction: disnake.Interaction):
    if interaction.user.id == self.ctx.author.id:
        embed = disnake.Embed(
            title="Доступные команды",
            description=f"**Развлечения**\n\n"
                        f"Скоро..."
        )
        await interaction.response.edit_message(embed=embed, view=self)
    else:
        await interaction.response.send_message("Вы не можете использовать эту кнопку!", ephemeral=True)


# Хелп
@bot.slash_command(name='help', aliases=["хелп", "помощь"], description='Help on the bot.')
async def help(ctx):
    conn = sqlite3.connect('language.db')
    c = conn.cursor()
    c.execute('SELECT language FROM settings WHERE guild_id = ?', (ctx.guild.id,))
    result = c.fetchone()
    language = result[0] if result else "English"
    conn.close()

    if result and result[0] == 'English':
        embed = disnake.Embed(
            description="> QuickAI Information Panel\n\n> <:moderation:1185044178854498455> **Permissions** - necessary permissions for the bot to work correctly\n> <:settings:1185670323740360765> **Settings** - help with setting up and communicating with the bot",
            color=0xffffff
        )
    else:
        embed = disnake.Embed(
            description="> QuickAI Информационная панель\n\n> <:moderation:1185044178854498455> **Права** - необходимые права для корректной работы бота\n> <:settings:1185670323740360765> **Настройки** - помощь в настройке и общении с ботом",
            color=0xffffff
        )

    view = HelpView(ctx)
    message = await ctx.send(embed=embed, view=view)

    await asyncio.sleep(300)  
    view.stop()  
    for child in view.children:
        child.disabled = True  
    await message.edit(view=view)  

    await ctx.send(embed=embed)
    
bot.run('BOT-TOKEN')

# Функционал от нас:
# 1. Рандом ключ на каждый запрос для избежания рейт лимита на ключ
# 2. Английский/Русский интерфейс
# 3. Система безопасности (недоработана)

# Теперь ваша очередь!
# Что осталось настроить?:
# 1. Сделать команду для переключения языков
# 2. Купить ключи от OpenAI, или настроить отправку запросов стороннему провайдеру
# 3. Разбросать по когам (по вашему желанию)
# 4. Удалить ненужные библиотеки