import discord
from discord.ext import commands
import asyncio
import sys

# Your bot token
TOKEN = 'YOUR_TOKEN_HERE'
# Your Discord user ID
MY_ID = YOUR_ID_HERE # Put your ID here so the bot wont ban you
# Replace with your server's ID
GUILD_ID = YOUR_SERVER_HERE  # e.g., 123456789012345678

# Set up intents
intents = discord.Intents.default()
intents.members = True  # Needed to access member list

# Initialize bot
bot = commands.Bot(command_prefix='!', intents=intents)

# Store the guild object for later use
guild = None

@bot.event
async def on_ready():
    global guild
    print(f'Logged in as {bot.user}')
    try:
        guild = bot.get_guild(GUILD_ID)
        if guild is None:
            print(f"Error: Could not find guild with ID {GUILD_ID}. Make sure the bot is in the server and the ID is correct.")
            await bot.close()
            return
        print(f"Connected to guild: {guild.name} (ID: {guild.id})")
        print("Type 'ban' in the terminal to ban everyone except you.")
    except Exception as e:
        print(f"Error in on_ready: {e}")
        await bot.close()

async def ban_everyone():
    if guild is None:
        print("Guild not found. Cannot proceed with banning.")
        return
    
    print("Starting ban process...")
    
    # Get the list of members to ban
    members_to_ban = [member for member in guild.members if member.id != MY_ID and member.id != bot.user.id]
    total_members = len(members_to_ban)
    print(f"Found {total_members} members to ban.")

    if total_members == 0:
        print("No members to ban.")
        return

    # Process bans in batches to avoid rate limits
    batch_size = 10  # Number of bans to process concurrently
    delay_between_batches = 0.5  # Delay in seconds between batches to avoid rate limits

    for i in range(0, total_members, batch_size):
        batch = members_to_ban[i:i + batch_size]
        print(f"Processing batch {i // batch_size + 1} of {(total_members - 1) // batch_size + 1}...")

        # Create a list of ban tasks for this batch
        ban_tasks = []
        for member in batch:
            ban_tasks.append(ban_member(member))
        
        # Run all ban tasks in this batch concurrently
        await asyncio.gather(*ban_tasks)

        # Add a small delay between batches to avoid rate limits
        if i + batch_size < total_members:  # Only delay if there are more batches
            await asyncio.sleep(delay_between_batches)

    print("Ban process complete")

async def ban_member(member):
    try:
        await member.ban(reason="Test ban")
        print(f"Banned {member.name}#{member.discriminator}")
    except discord.Forbidden:
        print(f"Failed to ban {member.name}#{member.discriminator} - Missing permissions")
    except discord.HTTPException as e:
        print(f"HTTP error banning {member.name}#{member.discriminator}: {e}")
    except Exception as e:
        print(f"Error banning {member.name}#{member.discriminator}: {e}")

async def terminal_input_loop():
    while True:
        command = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
        command = command.strip().lower()
        if command == "ban":
            await ban_everyone()
        elif command == "exit":
            print("Shutting down bot...")
            await bot.close()
            break
        else:
            print("Unknown command. Type 'ban' to ban everyone or 'exit' to shut down.")

# Main function to run the bot and terminal input loop
async def main():
    try:
        await bot.start(TOKEN)
    except Exception as e:
        print(f"Error starting bot: {e}")
    finally:
        if not bot.is_closed():
            await bot.close()

# Run the bot and terminal input loop
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.create_task(terminal_input_loop())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Received keyboard interrupt, shutting down...")
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()