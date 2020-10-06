from discord.ext import commands
import discord
import aiohttp
import os

SERVER = os.getenv("SERVER")
SECRET = os.getenv("SUNBOT_SECRET")

class Registration(commands.Cog):
    """Commands !"""
    def __init__(self, bot):
        self.bot = bot
        self.guild_id = 737845782992126032
        self.role_ids = [750436508871163951, 750435194166706337]
        self.check_in_id = 763107863572381717

    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = self.bot.get_guild(self.guild_id)
        self.roles = [self.guild.get_role(role) for role in self.role_ids]
        print("[REGISTRATION] Setup Registration check-in")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id == self.check_in_id:
            if payload.emoji.name == "☀️":
                await payload.member.send("Thanks for starting check-in! What email did you use to register? Reply with `!checkin <email>` to confirm your registration. \n \n If you did not register go register at http://links.sunhacks.io/apply and message me with the command after you're done!")
                print(f"[REGISTRATION] Starting registration for {payload.member.name}#{payload.member.discriminator}")


    @commands.command()
    @commands.dm_only()
    async def checkin(self, ctx, email):
        """Checks in hacker registration

        Sends a verification email to the email to a registered hacker

        Parameters
        ----------
        email: email used in registration
        """
        async with aiohttp.ClientSession() as session:
            params = {
                "email": email,
                "id" : ctx.author.id,
                "username": ctx.author.name,
                "discriminator": ctx.author.discriminator
            }
            headers = {"Sunbot-Secret" : SECRET}

            async with session.post(SERVER+'/discord/verify', params = params, headers = headers) as resp:
                if resp.status == 201:
                    await ctx.send("Sent a verification code to your email! Please respond with `!verify <code>` to finish checkin")
                    print(f"[REGISTRATION] Sent verification to  {ctx.author.name}#{ctx.author.discriminator}")
                else:
                    print(f"[REGISTRATION] Unable to find registration for  {ctx.author.name}#{ctx.author.discriminator}")
                    raise commands.BadArgument(message="Unable to send an email to that address! Make sure it is the same email you used to register.")

    @checkin.error
    async def checkin_error_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'email':
                await ctx.send("You need to specify an email: `!checkin <email>`")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(error)
        else:
            print("[REGISTRATION] ERROR")
            print(error)


    @commands.command()
    @commands.dm_only()
    async def verify(self, ctx, code):
        """Verifys hacker emails

        Confirms verification codes to check hackers into sunhacks

        Parameters
        ----------
        code: code sent to email for verification
        """
        async with aiohttp.ClientSession() as session:
            params = {
                "code" : code,
                "id" : ctx.author.id
            }
            headers = {"Sunbot-Secret" : SECRET}

            async with session.post(SERVER+'/discord/confirm', params = params, headers = headers) as resp:
                if resp.status == 201:
                    member = self.guild.get_member(ctx.author.id)
                    await member.add_roles(*self.roles)
                    await ctx.send("You're all set! Welcome to sunhacks!")
                    print(f"[REGISTRATION] Member {ctx.author.name}#{ctx.author.discriminator} joined as Hacker")
                else:
                    raise commands.BadArgument(message="Could not confirm your email. Please try again later.")


    @verify.error
    async def verify_error_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'code':
                await ctx.send("You need to specify a verification code: `!verify <code>`")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(error)
        else:
            print(error)


def setup(bot):
    bot.add_cog(Registration(bot))
