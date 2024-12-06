import discord
from discord.ext import tasks
import requests
import asyncio

DISCORD_TOKEN = "TOKEN"
MESSAGE_CHANNEL_ID = 1311850749680160788
VOICE_CHANNELS = {
    'BTC': 1311848835663925318,
    'ETH': 1311848911689875496,
    'SOL': 1311848976034566174
}
CRYPTOCOMPARE_API = "https://min-api.cryptocompare.com/data/price"

class CryptoBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.voice_states = True
        super().__init__(intents=intents)

    async def setup_hook(self):
        self.crypto_tracker.start()
        self.voice_channel_updater.start()

    async def on_ready(self):
        print(f'{self.user} est connecté et prêt!')

    @tasks.loop(minutes=1)
    async def crypto_tracker(self):
        channel = self.get_channel(MESSAGE_CHANNEL_ID)
        if channel:
            message = "📊 Prix des cryptomonnaies:\n"
            
            for crypto in ['BTC', 'ETH', 'SOL']:
                params = {'fsym': crypto, 'tsyms': 'EUR'}
                response = requests.get(CRYPTOCOMPARE_API, params=params)
                if response.status_code == 200:
                    price = response.json()['EUR']
                    message += f"{crypto}: {price:,.2f}€\n"
            
            await channel.send(message)

    @tasks.loop(minutes=5)
    async def voice_channel_updater(self):
        prices = {}
        for crypto in VOICE_CHANNELS.keys():
            params = {'fsym': crypto, 'tsyms': 'EUR'}
            response = requests.get(CRYPTOCOMPARE_API, params=params)
            if response.status_code == 200:
                prices[crypto] = response.json()['EUR']

        for crypto, channel_id in VOICE_CHANNELS.items():
            channel = self.get_channel(channel_id)
            if channel and crypto in prices:
                new_name = f"{crypto}: {prices[crypto]:,.0f}€"
                try:
                    await channel.edit(name=new_name)
                    await asyncio.sleep(2)
                except discord.errors.HTTPException as e:
                    print(f"Erreur lors de la mise à jour du salon {crypto}: {e}")

client = CryptoBot()
client.run(DISCORD_TOKEN)
