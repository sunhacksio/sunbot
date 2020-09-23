from discord.ext import commands
import discord
import aiohttp

class Registration(commands.Cog):
    """Commands !"""
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
        self.check_in_id = 757675583814762578

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id == self.check_in_id:
            if payload.emoji.name == "💖":
                await payload.member.send("Thanks for starting check-in! What email did you use to register? Reply with `!checkin <email>` to confirm your registration. \n \n If you did not register go register at http://links.sunhacks.io/apply and message me with the command after you're done!")


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
            async with session.post('http://127.0.0.1:5000/api/discord/verify', params=params) as resp:
                if resp.status == 201:
                    await ctx.send("Sent a verification code to your email! Please respond with `!verify <code>` to finish checkin")
                else:
                    raise commands.BadArgument(message="Unable to send an email to that address! Make sure it is the same email you used to register.")

    @checkin.error
    async def checkin_error_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'email':
                await ctx.send("You need to specify an email: `!checkin <email>`")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(error)


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
            async with session.post('http://127.0.0.1:5000/api/discord/confirm', params=params) as resp:
                if resp.status == 201:
                    await ctx.send("You're all set! Welcome to sunhacks!")
                else:
                    raise commands.BadArgument(message="Could not confirm your email. Please try again later.")


    @verify.error
    async def verify_error_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'email':
                await ctx.send("You need to specify a verification code: `!verify <code>`")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(error)


def setup(bot):
    bot.add_cog(Registration(bot))
