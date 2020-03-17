#!/usr/bin/env python3

import os
import sys
import json
from collections import deque

import asyncio
import discord
import youtube_dl
import datetime, time
import datetime

from discord.ext import commands

from QueueEntry import QueueEntry

# Options adapted from audio example in the discord.py repo
ydl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloaded',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ydl = youtube_dl.YoutubeDL(ydl_format_options)
ies = youtube_dl.extractor.gen_extractors()
queue = deque()
skip_votes = set()
timer = None
video_playing = None
try:
    with open("config.json") as c:
        config = json.load(c)
except FileNotFoundError:
    print("Config file not found - please copy config.json.example to config.json")
    sys.exit()

bot = commands.Bot( command_prefix=config['prefix'],
                    max_messages=100)
bot.playing = False

player_volume = 1

def supported(url):
    for ie in ies:
        if ie.suitable(url) and ie.IE_NAME != 'generic':
            # Site has dedicated extractor
            return True
    return False

@bot.event
async def on_ready():
    if len(sys.argv) > 1:
        try:
            channel = bot.get_channel(int(sys.argv[1]))
            embed = discord.Embed(title="🛠 **재시작 : Restart**", description="- - - - - - - - - - - - - - - - - - -",color=0x28b3fd, timestamp=datetime.datetime.utcnow())
            embed.add_field(name="Code : FlameBot.Restart",value="봇이 재시작 되었습니다 이와 같은 문구가 계속 나올시 아래의 DM으로 문의해주세요", inline=True)
            embed.set_footer(text="FlameTroll#1944",icon_url="https://cdn.discordapp.com/avatars/284159810860220416/ce814298f1dc715ef548d3bcca335c0a.png")
            restartmsg = await channel.send(embed=embed)
            await asyncio.sleep(10)
            await restartmsg.delete()
            await channel.send("재시작 - **봇이 재시작 되었습니다** 이와 같은 문구가 계속 나올시 `FlameTroll#1944` 로 문의해주세요")
        except:
            pass

@commands.has_permissions(administrator=True)
@bot.command(hidden=True)
async def restart(ctx):
    await ctx.send("봇이 재시작 되었습니다")
    os.execv(__file__, [__file__, str(ctx.channel.id)])

@bot.command()
async def 들어와(ctx):
    voice = ctx.author.voice
    if not voice:
        embed = discord.Embed(title="⛔ **오류 : Error**", description="- - - - - - - - - - - - - - - - - - -", color=0x28b3fd,timestamp=datetime.datetime.utcnow())
        embed.add_field(name="ErrorCode = voice_channel has no player", value="**음성채널에 들어가 있는지 확인해주세요**\n문제가 지속된다면 아래의 DM으로 문의해주세요", inline=True)
        embed.set_footer(text="FlameTroll#1944",icon_url="https://cdn.discordapp.com/avatars/284159810860220416/ce814298f1dc715ef548d3bcca335c0a.png")
        joinmsg = await ctx.send(embed=embed)
        await asyncio.sleep(10)
        await joinmsg.delete()
        await ctx.send("오류 : Error - **음성 채널에 들어가 있는지 확인해주세요** 문제가 지속될 경우 `FlameTroll#1944` 로 문의해주세요")

    elif ctx.voice_client:
        await ctx.voice_client.move_to(voice.channel)
    else:
        await voice.channel.connect()

@bot.command()
async def 나가(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        embed = discord.Embed(title="⛔ **오류 : Error**", description="- - - - - - - - - - - - - - - - - - -",color=0x28b3fd, timestamp=datetime.datetime.utcnow())
        embed.add_field(name="ErrorCode = No FlameBot in voine_channel",value="**음성채널에 봇이 없습니다**\n문제가 지속된다면 아래의 DM으로 문의해주세요", inline=True)
        embed.set_footer(text="FlameTroll#1944",icon_url="https://cdn.discordapp.com/avatars/284159810860220416/ce814298f1dc715ef548d3bcca335c0a.png")
        outmsg = await ctx.send(embed=embed)
        await asyncio.sleep(10)
        await outmsg.delete()
        await ctx.send("오류 : Error - **음성채널에 봇이 없습니다** 문제가 지속될 경우 `FlameTroll#1944` 로 문의해주세요")


async def play_internal(ctx, video):
    global timer
    try:
        os.remove("downloaded")
    except FileNotFoundError:
        pass
    ydl.download([video.url])
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("downloaded", options="-b:a 96k -threads 0"))
    await ctx.send(await commands.clean_content().convert(ctx,
                                    "현재 재생중인 곡 : {}".format(video.name)))
    ctx.voice_client.play(source)
    timer = time.time()
    ctx.voice_client.source.volume = player_volume
    while ctx.voice_client and ctx.voice_client.is_playing():
        await asyncio.sleep(2)

@bot.command()
async def 재생(ctx, *, url):
    voice = ctx.author.voice
    if not voice:
        embed = discord.Embed(title="⛔ **오류 : Error**", description="- - - - - - - - - - - - - - - - - - -",color=0x28b3fd, timestamp=datetime.datetime.utcnow())
        embed.add_field(name="ErrorCode = voice_channel has no player",value="**음성채널에 들어가 있는지 확인해주세요**\n문제가 지속된다면 아래의 DM으로 문의해주세요", inline=True)
        embed.set_footer(text="FlameTroll#1944",icon_url="https://cdn.discordapp.com/avatars/284159810860220416/ce814298f1dc715ef548d3bcca335c0a.png")
        playmsg = await ctx.send(embed=embed)
        await asyncio.sleep(10)
        await playmsg.delete()
        await ctx.send("오류 : Error - **음성 채널에 들어가 있는지 확인해주세요** 문제가 지속될 경우 `FlameTroll#1944` 로 문의해주세요")

    elif ctx.voice_client:
        await ctx.voice_client.move_to(voice.channel)
    else:
        await voice.channel.connect()

    global video_playing
    global timer
    if not ctx.voice_client:
        embed = discord.Embed(title="⛔ **오류 : Error**", description="- - - - - - - - - - - - - - - - - - -",color=0x28b3fd, timestamp=datetime.datetime.utcnow())
        embed.add_field(name="ErrorCode = Not at player in voice_chaanel",value="**먼저 !들어와 명령어를 통해 봇을 넣어주세요**\n문제가 지속된다면 아래의 DM으로 문의해주세요", inline=True)
        embed.set_footer(text="FlameTroll#1944",icon_url="https://cdn.discordapp.com/avatars/284159810860220416/ce814298f1dc715ef548d3bcca335c0a.png")
        msg1 = await ctx.send(embed=embed)
        await asyncio.sleep(10)
        await msg1.delete()
        return
    if not supported(url):
        url = f"ytsearch1:{url}"
    metadata = ydl.extract_info(url, download=False)
    if '_type' in metadata and metadata['_type'] == "playlist":
        metadata = metadata['entries'][0]
    queue.appendleft(QueueEntry(metadata['title'], metadata['webpage_url'], ctx.author.name, metadata['duration']))
    embed = discord.Embed(title="재생 대기중... : **{}**".format(metadata['title']), description="- - - - - - - - - - - - - - - - - - -", color=0x28b3fd,timestamp=datetime.datetime.utcnow())
    embed.set_footer(text="FlameTroll#1944",icon_url="https://cdn.discordapp.com/avatars/284159810860220416/ce814298f1dc715ef548d3bcca335c0a.png")
    msg2 = await ctx.send(embed=embed)
    await asyncio.sleep(10)
    await msg2.delete()

    if bot.playing: return
    bot.playing = True
    while queue and bot.playing:
        skip_votes.clear()
        video = queue.pop()
        video_playing = video
        await play_internal(ctx, video)
    bot.playing = False
    video_playing = None
    timer = None

@bot.command()
async def 멈춰(ctx):
    if bot.playing:
        ctx.voice_client.stop()
        bot.playing = False
        queue.clear()
        await ctx.send("노래 대기열과 현재 재생중인 노래가 삭제 되었습니다")
    else:
        embed = discord.Embed(title="⛔ **오류 : Error**", description="- - - - - - - - - - - - - - - - - - -",color=0x28b3fd, timestamp=datetime.datetime.utcnow())
        embed.add_field(name="ErrorCode = The song is not running",value="**아무 노래도 실행중이지 않습니다**\n문제가 지속된다면 아래의 DM으로 문의해주세요", inline=True)
        embed.set_footer(text="FlameTroll#1944",icon_url="https://cdn.discordapp.com/avatars/284159810860220416/ce814298f1dc715ef548d3bcca335c0a.png")
        stopmsg = await ctx.send(embed=embed)
        await asyncio.sleep(10)
        await stopmsg.delete()
        await ctx.send("오류 : Error - **아무노래도 실행중이지 않습니다** 문제가 지속될 경우 `FlameTroll#1944` 로 문의해주세요")

@bot.command()
async def 스킵(ctx):
    if bot.playing:
        if ctx.author == ctx.guild.owner:
            ctx.voice_client.stop()
            await ctx.send("서버 주인에 의해 투표 없이 스킵되었습니다")
        else:
            skip_votes.add(ctx.author)
            await ctx.send("스킵 하기 위해 투표를 추가 했습니다 - 현재 투표: {}. 필요한 투표 수 : {}".format(len(skip_votes), len(ctx.voice_client.channel.members) // 2))
            if len(skip_votes) >= len(ctx.voice_client.channel.members) // 2:
                ctx.voice_client.stop()
                await ctx.send("투표에 의해 스킵되었습니다")
    else:
        await ctx.send("아무노래도 실행중이지 않습니다")

@bot.command(aliases=['vol'])
async def 볼륨(ctx, *, vol=None):
    global player_volume

    if not vol:
        await ctx.send(f"현재 볼륨 : {player_volume * 100}")
        await ctx.send("볼륨 명령어에 오류가 생겨 이용이 불가 합니다 (ㅡㅡ)")
        return

    if ctx.voice_client and ctx.voice_client.source:
        ctx.voice_client.source.volume = int(vol)/100

    player_volume = inot(vl)/100

@bot.command(aliases=['queue'])
async def 대기열(ctx):
    msg = "대기열: ```"
    for s in queue:
        msg += f"{s.name} 요청자 : {s.author}\n"
    await ctx.send(await commands.clean_content().convert(ctx, msg + "```"))


@bot.command(aliases=['np'])
async def 현재곡(ctx):
    timeconv = lambda t: datetime.timedelta(seconds=int(t))
    if video_playing:
        await ctx.send(f"현재 재생중인 곡 : `{video_playing.name}`, 명령자 : `{video_playing.author}.` 시간 : `{timeconv(time.time() - timer)}/{timeconv(video_playing.duration)}`.")
    else:
        await ctx.send("에러 : Error - `아무 노래도 실행 중이지 않습니다`")


bot.run("NjgyMTcxNzM2OTk2ODM5NDMw.XmTh4g.Rx9VPuw57fGWCTEZdQKcoOo99ac")
