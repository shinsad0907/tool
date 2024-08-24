import discord
from discord.ext import commands
from discord.ui import View,Button
from key import getkey
from github import github
import asyncio
import requests
from discord.ext import commands, tasks
import pytz
from datetime import datetime, timedelta, timezone
import aiohttp
import os,json
from upload import upload
# Thay thế token của bạn
TOKEN = 'MTI3MDE1NzE5MjI3OTg4Mzg5Nw.G9f6Mm.HMGPvaEPDiIMl-4nQa5AXUEzx-np3x2NqtorZA'

# Tạo đối tượng Intents
intents = discord.Intents.default()
intents.message_content = True  # Bật quyền truy cập nội dung tin nhắn

# Khởi tạo bot với intents
bot = commands.Bot(command_prefix='!', intents=intents)

# View cho lựa chọn chính
class MainOptionsView(View,discord.Client):
    def __init__(self):
        super().__init__()

    async def send_main_message(self, channel: discord.abc.Messageable):
        embed = discord.Embed(
            title="📢 **Help Menu & Important Notice**",
            description=(
                "🔐 **Authentication**\n"
                "Use the `@Bot MMO /login` command to authenticate with the key purchased from the bot admin.\n\n"

                "📱 **Reup Actions**\n"
                "Use the `/connect` command to get cookies with social network accounts to perform reup actions as follows:\n\n"
                "- 🔴 **Facebook**: `@Bot MMO /connect facebook user`\n"
                "- 🔴 **FanPage Facebook**: `@Bot MMO /connect facebook page`\n"
                "- 🐦 **Twitter**: `@Bot MMO /connect twitter`\n"
                "- 📸 **Instagram**: `@Bot MMO /connect instagram`\n"
                "- 🎥 **YouTube**: `@Bot MMO /connect youtube`\n"
                "- 🎵 **TikTok**: `@Bot MMO /connect tiktok`\n\n"

                "📱 **Display Cookies**\n"
                "Use the `/cookies` command to display cookies taken from social network accounts as follows:\n\n"
                "- 🔴 **Facebook**: `@Bot MMO /cookies facebook`\n"
                "- 🐦 **Twitter**: `@Bot MMO /cookies twitter`\n"
                "- 📸 **Instagram**: `@Bot MMO /cookies instagram`\n"
                "- 🎥 **YouTube**: `@Bot MMO /cookies youtube`\n"
                "- 🎵 **TikTok**: `@Bot MMO /cookies tiktok`\n"
                "- ............\n\n"

                "📅 **Event Management**\n"
                f"Use the `/event` command to create and manage events, track the number of posts, and monitor interactions during a specific time period. Here's how to use it:\n\n"
                "`/event create --channel [channel_name] --name_even [event_name] --description [description] --interact [interaction_threshold]`\n\n"
                "- **Channel Name**: The name of the channel where the event will take place.\n"
                "- **Event Name**: The name of the event.\n"
                "- **Description**: A brief description of the event.\n"
                "- **Interaction Threshold**: The number of interactions required to trigger the event.\n\n"
                
                "📤 **Upload Content** 📤\n"
                "After selecting the top content, use the `/upload` command to upload the content with a custom status to social networks. Here's how to use it:\n\n"
                "`/upload --id_message [id_message] --status [status]`\n\n"
                "- **id_message**: The ID of the message containing the content you wish to upload.\n"
                "- **status**: The status or caption you want to add to the content when uploading.\n\n"
                "For example, to upload a message with ID 1234567890 and the status 'Check out this amazing post!', use:\n"
                "`/upload --id_message 1234567890 --status 'Check out this amazing post!'`\n"
                "This command allows you to customize the post before sharing it on social media platforms."
            
            ),
            color=discord.Color.blue()  # Chọn màu sắc phù hợp
        )

        
        # Gửi thông báo với Embed và View
        await channel.send(embed=embed, view=self)
    

    @bot.event
    async def select_top(self, message):
        def check(m):
            return m.author == message.author and m.channel == message.channel
        async def download_image(attachment, save_path):
            async with aiohttp.ClientSession() as session:
                async with session.get(attachment.url) as resp:
                    if resp.status == 200:
                        with open(save_path, 'wb') as f:
                            f.write(await resp.read())
                        print(f"Image saved to {save_path}")
                    else:
                        print(f"Failed to download image from {attachment.url}")

        try:
            # Tạo embed yêu cầu người dùng chọn số Top
            prompt_embed = discord.Embed(
                title="🎯 **Select Top Image** 🎯",
                description=(
                    "The event has concluded, and we have the top images with the most reactions! 🎉\n\n"
                    "Please select the Top number (1, 2, or 3) by replying with the number corresponding to your choice.\n"
                    "For example: `1` for Top #1, `2` for Top #2, and `3` for Top #3.\n\n"
                    "You have 60 seconds to make your selection."
                ),
                color=discord.Color.blue()  # Màu xanh dương cho sự chuyên nghiệp
            )
            await message.channel.send(embed=prompt_embed)

            # Chờ người dùng nhập thông tin
            user_response = await bot.wait_for('message', check=check, timeout=60)
            top_number = int(user_response.content.strip())  # Nhận số Top từ người dùng
            print(top_number)

            # Lấy dữ liệu từ URL JSON
            url = "https://raw.githubusercontent.com/shinsad0907/MMO/main/EVEN.json"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                
                for guild in bot.guilds:
                    server_name = guild.name
                    if server_name in data:
                        event_data = data[server_name]
                        start_time_str = event_data.get("Start_Time")
                        end_time_str = event_data.get("End_Time")
                        name_channel = event_data.get("Name_chanel")
                        name_event = event_data.get("Name_even")

                        # Chuyển đổi chuỗi thời gian thành đối tượng datetime
                        tz = pytz.timezone('Asia/Ho_Chi_Minh')
                        start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
                        end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M")
                        start_time = tz.localize(start_time)
                        end_time = tz.localize(end_time)

                        channel = discord.utils.get(guild.channels, name=name_channel)
                        admin = discord.utils.get(guild.channels, name='bot_setup')

                        if channel is None:
                            print(f"Channel {name_channel} not found.")
                            return

                        if admin is None:
                            print(f"Admin with name bot_setup not found.")
                            return

                        messages_with_reactions = []

                        async for msg_in_history in channel.history(after=start_time, before=end_time, limit=100):
                            total_reactions = sum(reaction.count for reaction in msg_in_history.reactions)
                            if total_reactions > 0:
                                messages_with_reactions.append((msg_in_history, total_reactions))

                        # Sắp xếp danh sách tin nhắn theo số lượng phản ứng giảm dần
                        messages_with_reactions.sort(key=lambda x: x[1], reverse=True)

                        top_messages = messages_with_reactions[:top_number]  # Lấy Top N tin nhắn

                        if top_messages:
                            # Tìm tin nhắn tương ứng với Top number từ người dùng
                            selected_message = None
                            for i, (message, reactions) in enumerate(top_messages):
                                if i == top_number - 1:
                                    selected_message = message
                                    break

                            if selected_message:
                                if selected_message.attachments:
                                    # Gửi các tệp đính kèm
                                    for self.attachment in selected_message.attachments:
                                        embed = discord.Embed(
                                            description=(
                                                f"📸 **Top #{top_number}**\n**This image has {reactions} reactions.**"
                                            ),
                                            color=discord.Color.blue()
                                        )
                                        # Gửi thông báo với embed
                                        await admin.send(embed=embed, file=await self.attachment.to_file())
                                        server_name = message.guild.name
                                        new_filename = f"{server_name}.jpg"  # Đặt tên mới cho file, bạn có thể tùy chỉnh
                                        save_path = os.path.join(f"./{server_name}", new_filename)
                                        await download_image(self.attachment, save_path)
                                else:
                                    # Tạo embed cho tin nhắn văn bản
                                    embed1 = discord.Embed(
                                        description=(
                                            f"📸 **Top #{top_number}**\n**This message has {reactions} reactions.**\n{selected_message.content}"
                                        ),
                                        color=discord.Color.blue()
                                    )
                                    # Gửi thông báo với embed
                                    await admin.send(embed=embed1)
                            embed_ask_upload = discord.Embed(
                                title="📤 **Upload to Social Media**",
                                description="Do you want to upload the image or content to social media? Use the command:\n`/upload [facebook, tiktok, instagram, ytb, twitter]`",
                                color=discord.Color.blue()
                            )
                            await message.channel.send(embed=embed_ask_upload)

                            def check(m):
                                return m.author == message.author and m.channel == message.channel
                            user_response = await bot.wait_for('message', check=check, timeout=60)
                        else:
                            print("No messages found with reactions.")
        except Exception as e:
            print(f"An error occurred: {e}")
    async def download_attachments_from_message(self, message_id, save_path):
        found_message = None

        # Duyệt qua tất cả các kênh trong tất cả các guilds
        for guild in bot.guilds:
            for channel in guild.text_channels:  # Chỉ duyệt qua các text channel
                try:
                    # Fetch the message by ID
                    message = await channel.fetch_message(message_id)
                    if message:
                        found_message = message
                        break
                except (discord.NotFound, discord.Forbidden):
                    continue  # Nếu không tìm thấy tin nhắn hoặc không có quyền, tiếp tục duyệt các kênh khác
            if found_message:
                break

        if not found_message:
            print(f"Message with ID {message_id} not found in any accessible channel.")
            return

        # Kiểm tra và tải xuống các tệp đính kèm
        if found_message.attachments:
            for attachment in found_message.attachments:
                if attachment.filename.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', 
                                                '.mp4', '.mov', '.avi', '.wmv', '.mkv')):
                    file_url = attachment.url
                    self.file_name = attachment.filename

                    async with aiohttp.ClientSession() as session:
                        async with session.get(file_url) as response:
                            if response.status == 200:
                                file_data = await response.read()
                                with open(os.path.join(save_path, self.file_name), 'wb') as file:
                                    file.write(file_data)
                                    print(f"File saved as {self.file_name}")
                                    return True
                            else:
                                print(f"Failed to download file: {response.status}")
        else:
            print(f"No attachments found in message {message_id}.")

    async def upload(self,message_id,server_name,status):
        if await self.download_attachments_from_message(message_id,'./uploads'):
            upload().upload(server_name,status,self.file_name)

    @bot.event
    async def save_token(self, message, TYPE, platform):
        if message.attachments:
            # Nếu cookie được gửi dưới dạng file đính kèm
            attachment = message.attachments[0]
            if attachment.filename.endswith('.txt'):
                file_content = await attachment.read()
                cookie = file_content.decode('utf-8').strip()
        else:
            # Nếu cookie được gửi trực tiếp trong nội dung tin nhắn
            try:
                cookie = message.content.lower().split('/connect facebook user ')[1]
            except IndexError:
                await message.channel.send("Không tìm thấy cookie trong tin nhắn. Vui lòng kiểm tra lại.")
                return
        print(f"Cookie nhận được: {cookie}")
        try:
        

            server_name = message.author.guild.name
            print(TYPE, platform)

            if github().save_data(server_name, TYPE, platform, cookie) == True:
                embed = discord.Embed(
                    title="✅ **Token Saved Successfully**",
                    description=(
                        f"Your token for **{platform}** has been successfully saved. 🎉\n\n"
                        "**Important:** Keep your token secure and do not share it publicly."
                        "\n🔔 **Note:** Please wait 5 minutes for the token to update" 
                    ),
                    color=discord.Color.green()  # Màu xanh lá cây để biểu thị thành công
                )
                await message.channel.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="Token Save Failed",
                    description=(
                        "❌ **Token Save Failed!**\n\n"
                        f"The token **{cookie}** is invalid or incorrect."
                    ),
                    color=discord.Color.red()  # Màu đỏ để biểu thị thất bại
                )
                await message.channel.send(embed=embed)

        except TimeoutError:
            await message.channel.send(f"Bạn đã hết thời gian để phản hồi. Vui lòng thử lại lệnh `/connect {platform}`.")

    async def wait_for_message(ctx, prompt, timeout=60):
        """
        Hỗ trợ chờ tin nhắn của người dùng với một thông báo và thời gian chờ.
        """
        await ctx.send(prompt)
        try:
            msg = await bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=timeout)
            if msg.content == '/reset':
                return None  # Trả về None nếu lệnh /reset được sử dụng
            return msg.content
        except asyncio.TimeoutError:
            await ctx.send("Lỗi: Thời gian chờ đã hết.")
            return None

    @bot.event
    async def save_even(self, message, TYPE, platform):
        try:
            if message.attachments:
                # Nếu cookie được gửi dưới dạng file đính kèm
                attachment = message.attachments[0]
                if attachment.filename.endswith('.txt'):
                    file_content = await attachment.read()
                    cookie = file_content.decode('utf-8').strip()
            else:
                # Nếu cookie được gửi trực tiếp trong nội dung tin nhắn
                try:
                    cookie = message.content.lower().split('/event create')[1]
                except IndexError:
                    await message.channel.send("Không tìm thấy cookie trong tin nhắn. Vui lòng kiểm tra lại.")
                    return

            print(cookie)

            # Lấy thông tin từ cookie
            channel_name = cookie.split('--channel ')[1].split(' ')[0]
            name_even = cookie.split('--name_even ')[1].split(' ')[0] if '--name_even ' in cookie else ''
            description = cookie.split('--description ')[1].split(' ')[0] if '--description ' in cookie else ''
            start_date = cookie.split('--start_date ')[1].split(' ')[0] if '--start_date ' in cookie else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            interact = cookie.split('--interact ')[1].split(' ')[0]

            server_name = message.guild.name

            # Gọi hàm save_data để lưu thông tin event vào GitHub
            if github().save_data(server_name, TYPE, platform, f'{channel_name}|{name_even}|{description}|{start_date}|{interact}'):
                embed = discord.Embed(
                    title="🎉 Event Saved Successfully!",
                    description=(
                        f"**Name Channel:** {channel_name}\n"
                        f"**Event Name:** {name_even}\n"
                        f"**Description:** {description}\n"
                        f"**Start Time:** {start_date}\n"
                        f"**Iteract:** {interact}\n"
                        "Your event has been created and saved successfully! 🎉\n"
                        "Make sure to monitor the interactions and posts during this event."
                    ),
                    color=discord.Color.green()
                )
                await message.channel.send(embed=embed)

                # Tìm kênh dựa trên tên kênh
                channel = discord.utils.get(message.guild.channels, name=channel_name)

                if channel is not None:
                    embed = discord.Embed(
                        title="📅 **Upcoming Event Announcement!**",
                        description=(
                            f"💬 **Description:** {description}\n\n"
                            f"📸 **Start Date:** {start_date}\n\n"
                            "🎯 **Event Rules:**\n"
                            f"- Only photos or videos with more than {interact} interactions will be posted on social media.\n"
                            "- Please note that only videos created within the last month will be considered for this event.\n\n"
                            "Good luck and let's create some memorable moments together!"
                        ),
                        color=discord.Color.purple()  # Màu tím để tạo cảm giác trang trọng và hào hứng
                    )
                    await channel.send(embed=embed)
                else:
                    await message.channel.send(f"Channel {channel_name} not found.")
            else:
                await message.channel.send(f"Failed to save event data for {server_name}.")
        
        except Exception as e:
            await message.channel.send(f"An error occurred: {str(e)}")

async def checkupload(bot):
    messages_file_path = 'messages_with_reactions.json'
    upload_file_path = 'upload.json'
    
    try:
        # Đọc dữ liệu từ file messages_with_reactions.json
        with open(messages_file_path, 'r') as json_file:
            messages_data = json.load(json_file)
        
        # Đọc dữ liệu từ file upload.json
        with open(upload_file_path, 'r') as json_file:
            upload_data = json.load(json_file)
        
        now = datetime.now(timezone.utc)  # Thời gian hiện tại
        one_hour_ago = now - timedelta(hours=1)  # Thời gian một giờ trước
        
        # Lưu ID tin nhắn đã được upload
        uploaded_message_ids = set()
        for ids in upload_data.values():
            uploaded_message_ids.update(ids)
        
        # Kiểm tra tin nhắn trong messages_with_reactions.json
        for server_name, channels in messages_data.items():
            for channel_name, messages in channels.items():
                print(f"Checking channel: {channel_name} in server: {server_name}")
                for message_id, message_data in messages.items():
                    timestamp = datetime.fromisoformat(message_data["timestamp"])
                    
                    # Kiểm tra nếu thời gian tin nhắn đã vượt quá một giờ
                    if timestamp < one_hour_ago:
                        # Tin nhắn đã quá thời gian một giờ
                        if message_id not in uploaded_message_ids:
                            print(f"Message ID {message_id} in server {server_name} and channel {channel_name} has exceeded one hour and has not been uploaded yet.")
                            # Thực hiện các hành động khác nếu cần, ví dụ gửi thông báo hoặc thêm vào upload.json
                            # view = MainOptionsView()
                            # await view.upload(message_id,server_name,'')
                    else:
                        print(f"Message ID {message_id} in server {server_name} and channel {channel_name} has not exceeded one hour yet.")
    except FileNotFoundError as e:
        print(f"File not found: {e.filename}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON file: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

async def get_messages_with_reactions(channel,Iteract):
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(days=30)
    
    messages_with_reactions = []

    async for message in channel.history(after=start_time, limit=None):
        total_reactions = sum(reaction.count for reaction in message.reactions)
        if total_reactions > int(Iteract):
            messages_with_reactions.append((message, total_reactions))
    
    return messages_with_reactions
async def checkeven(bot):
    messages_file_path = 'messages_with_reactions.json'
    events_url = 'https://raw.githubusercontent.com/shinsad0907/MMO/main/EVEN.json'  # Đường dẫn đến file JSON trên GitHub
    
    # Lấy dữ liệu từ GitHub thông qua URL
    response = requests.get(events_url)
    events_data = response.json()

    # Kiểm tra sự tồn tại của file và đọc dữ liệu nếu có
    if os.path.exists(messages_file_path):
        with open(messages_file_path, 'r') as json_file:
            data = json.load(json_file)
    else:
        print(f"File {messages_file_path} không tồn tại. Tạo file mới.")
        data = {}  # Tạo một dict rỗng nếu file không tồn tại

    data_to_save = data.copy()  # Sao chép dữ liệu hiện tại để cập nhật
    
    # Lấy danh sách các ID hiện có
    existing_ids = set(
        message_id
        for server in data.values()
        for channel in server.values()
        for message_id in channel
    )

    for guild in bot.guilds:
        server_name = guild.name
        if server_name in events_data:
            event_info = events_data[server_name]
            for name_channel, event_details in event_info.items():
                channel = discord.utils.get(guild.channels, name=name_channel)
                if channel:
                    messages_with_reactions = await get_messages_with_reactions(channel,event_details['Iteract'])
                    channel_data = {}
                    setup_channel = discord.utils.get(guild.channels, name='bot_setup')

                    for message, reactions in messages_with_reactions:
                        message_id_str = str(message.id)

                        if message_id_str in existing_ids:
                            continue  # Bỏ qua tin nhắn đã tồn tại

                        timestamp = message.created_at.isoformat()  # Lấy thời gian gửi tin nhắn
                        channel_data[message_id_str] = {
                            "reactions": reactions,
                            "timestamp": timestamp
                        }

                        # Gửi thông báo nếu chưa có thông báo trước đó
                        if setup_channel:
                            embed = discord.Embed(
                                title="📈 **High Interaction Alert**",
                                description=(
                                    f"[Click here to view the message](https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id})\n\n"
                                    f"Message ID: {message.id} has more than {event_details['Iteract']} interactions.\n\n"
                                    "Please write a status for this image or video to upload to social networks using the command:\n"
                                    "`/upload --id_message [id_message] --status [status]`\n\n"
                                    "If no status is provided within 1 hour, the bot will automatically post and set a default status."
                                ),
                                color=discord.Color.orange()
                            )
                            await setup_channel.send(embed=embed)

                    # Cập nhật dữ liệu mới vào file JSON
                    if channel_data:
                        if server_name not in data_to_save:
                            data_to_save[server_name] = {}
                        if name_channel not in data_to_save[server_name]:
                            data_to_save[server_name][name_channel] = {}

                        for message_id, msg_data in channel_data.items():
                            data_to_save[server_name][name_channel][message_id] = msg_data

    # Ghi dữ liệu vào file JSON, ghi đè dữ liệu cũ
    with open(messages_file_path, 'w') as json_file:
        json.dump(data_to_save, json_file, indent=4)

    print("Data đã được lưu thành công.")
@tasks.loop(minutes=1)  # Kiểm tra mỗi phút
async def check_events():
    await checkeven(bot)
    await checkupload(bot)

@bot.event
async def on_ready():
    print(f'Bot is ready as {bot.user}!')
    check_events.start()
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mention in message.content and 'help' in message.content.lower():
        view = MainOptionsView()
        await view.send_main_message(message.channel)
    if bot.user.mention in message.content and '/connect facebook user' in message.content.lower():
        view = MainOptionsView()
        await view.save_token(message,'TOKEN','user')
    if bot.user.mention in message.content and '/connect facebook page' in message.content.lower():
        view = MainOptionsView()
        await view.save_token(message,'TOKEN','page')
    if bot.user.mention in message.content and '/connect youtube' in message.content.lower():
        view = MainOptionsView()
        await view.save_token(message,'TOKEN','youtube')
    if bot.user.mention in message.content and '/connect tiktok' in message.content.lower():
        view = MainOptionsView()
        await view.save_token(message,'TOKEN','tiktok')
    if bot.user.mention in message.content and '/connect twitter' in message.content.lower():
        view = MainOptionsView()
        await view.save_token(message,'TOKEN','twitter')
    if bot.user.mention in message.content and '/connect instagram' in message.content.lower():
        view = MainOptionsView()
        await view.save_token(message,'TOKEN','instagram')
    if bot.user.mention in message.content and '/event create' in message.content.lower():
        view = MainOptionsView()
        await view.save_even(message,'EVEN','EVEN')
    if bot.user.mention in message.content and '/selecttop' in message.content.lower():
        view = MainOptionsView()
        await view.select_top(message)
    if bot.user.mention in message.content and '/upload' in message.content.lower():
        view = MainOptionsView()
        if message.attachments:
            # Nếu cookie được gửi dưới dạng file đính kèm
            attachment = message.attachments[0]
            if attachment.filename.endswith('.txt'):
                file_content = await attachment.read()
                cookie = file_content.decode('utf-8').strip()
        else:
            # Nếu cookie được gửi trực tiếp trong nội dung tin nhắn
            try:
                cookie = message.content.lower().split('/upload')[1]
            except IndexError:
                await message.channel.send("Không tìm thấy cookie trong tin nhắn. Vui lòng kiểm tra lại.")
                return
        id_message = cookie.split('--id_message ')[1].split(' ')[0]
        status = cookie.split('--status ')[1].split(' ')[0] if '--status ' in cookie else ''
        server_name = message.guild.name
        await view.upload(id_message,server_name,status)

    
        

    if bot.user.mention in message.content and '/login' in message.content.lower():
        def check(m):
            return m.author == message.author and m.channel == message.channel
        try:
            # Chờ người dùng nhập thông tin
            msg = await bot.wait_for('message', check=check, timeout=60)
            server_name = message.author.guild.name
            if getkey().getkey(msg.content,server_name) == True:
                embed = discord.Embed(
                    title="Login Success",
                    description=(
                        "🎉 **Login Successful!**\n\n"
                        f"key has been logged in successfully: **{msg.content}\n\n**"
                        "🔗 **Use the `/connect .....` command to enter your TOKEN key for saving TOKEN from social network platforms.**"
                    ),
                    color=discord.Color.green()  # Màu xanh lá cây để biểu thị thành công
                )
                await message.channel.send(embed=embed)
                github().createfile(server_name)
                server_name = message.guild.name
                os.makedirs(server_name, exist_ok=True)
            else:
                embed = discord.Embed(
                    title="Login Failed",
                    description=(
                        "❌ **Login Failed!**\n\n"
                    ),
                    color=discord.Color.red()  # Màu xanh lá cây để biểu thị thành công
                )
                await message.channel.send(embed=embed)
        
        except TimeoutError:
            await message.channel.send("Bạn đã hết thời gian để phản hồi. Vui lòng thử lại lệnh `/connect github`.")

    # Đảm bảo bot vẫn xử lý các lệnh khác
    await bot.process_commands(message)

# Chạy bot với token của bạn
bot.run(TOKEN)
