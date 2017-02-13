import asyncio
import sqlite3
import discord

class Bank:

	def __init__(self, dbname):
		self.dbname = dbname
		self.db = None
		self.cursor = None

	def opendb(self):
		try:
			self.db = sqlite3.connect(self.dbname)
			self.cursor = self.db.cursor()
		except:
			return -1

	def closedb(self):
		if not self.db: return -1
		self.db.close()

	def initialize(self):
		if not self.cursor: return -1
		self.cursor.execute('CREATE TABLE users (id integer primary key autoincrement, username text, credits int)')
		self.db.commit()

	def is_init(self):
		if not self.cursor: return -1
		for table in self.cursor.execute('SELECT * FROM sqlite_sequence'):
			if table[0] == 'users':
				return True
		return False

	def reset(self):
		if not self.cursor: return -1
		self.cursor.execute('DELETE FROM users')
		self.db.commit()

	def get_account_info(self, username):
		for account in self.cursor.execute('SELECT * FROM users'):
			if account[1] == username:
				return account
		return -1

	def add_account(self, username, credits=0):
		if (not self.cursor) or (self.get_account_info(username) != -1): return -1
		self.cursor.execute('INSERT INTO users (username, credits) VALUES ("{0}", {1})'.format(username, credits))
		self.db.commit()

	def add_credits(self, username, credits):
		if (not self.cursor) or (self.get_account_info(username) == -1): return -1
		account_info = self.get_account_info(username)
		account_credits = account_info[2]

		credits = account_credits + credits
		self.cursor.execute('UPDATE users SET credits={0} WHERE id={1}'.format(credits, account_info[0]))
		self.db.commit()

	def transfer(self, username_1, username_2, credits):
		if (not self.cursor) or (self.get_account_info(username_1) == -1) or (self.get_account_info(username_2) == -1): return -1

		self.add_credits(username_1, credits)
		self.add_credits(username_2, -credits)

	def delete_account(self, username):
		if (not self.cursor) or (self.get_account_info(username) == -1): return -1
		account_info = self.get_account_info(username)
		account_id = account_info[0]

		self.cursor.execute('DELETE FROM users WHERE id={0}'.format(account_id))
		self.db.commit()


class BankBot(discord.Client):

	def __init__(self, dbfile):
		discord.Client.__init__(self)
		self.bank = Bank(dbfile)

	@asyncio.coroutine
	async def on_ready(self):
		print('BankBot is running !')
		self.bank.opendb()
		try:
			if not self.bank.is_init(): self.bank.initialize()
		except:
			self.bank.initialize()

	@asyncio.coroutine
	async def on_message(self, message):
		user_id = message.author.id
		username = message.author.name + '#' + message.author.discriminator
		if message.content.startswith('$create_account'):
			if self.bank.add_account(user_id) == -1: await self.send_message(message.channel, '<@{}> sorry, but you already have a bank account'.format(user_id))
			else:
				await self.send_message(message.channel, '<@{}> you now have a bank account !'.format(user_id))

		if message.content.startswith('$account_info'):
			account_info = self.bank.get_account_info(user_id)
			if account_info == -1: await self.send_message(message.channel, '<@{}> sorry, but you have no bank account'.format(user_id))
			else:
				await self.send_message(message.channel, '*<@{}> account info*'.format(user_id))
				await self.send_message(message.channel, '**Client ID: {}**'.format(account_info[0]))
				await self.send_message(message.channel, '**Credits: {}$ **'.format(account_info[2]))

		if message.content.startswith('$transfer'):
			if self.bank.get_account_info(user_id) == -1: await self.send_message(message.channel, '<@{}> sorry, but you have no bank account'.format(user_id))
			else:
				user_id_2 = message.content[message.content.index('@')+1:message.content.index('>')]
				if (self.bank.get_account_info(user_id_2) == -1): 
					await self.send_message(message.channel, '<@{}> sorry, but the other user doesnt have bank account'.format(user_id))
				else:
					credits = message.content[message.content.index('!')+1:]
					if credits.isalpha(): await self.send_message(message.channel, '<@{}> sorry, credits are invalid'.format(user_id))
					else:
						if int(credits) < 0: await self.send_message(message.channel, '<@{}> sorry, you specified a negative amount of credits'.format(user_id))
						if int(credits) > self.bank.get_account_info(user_id)[2]: await self.send_message(message.channel, '<@{}> sorry, you doesnt have this amount of credits'.format(user_id))
						if self.bank.transfer(user_id_2, user_id, int(credits)) != -1: await self.send_message(message.channel, '<@{0}> you successfully transfered credits to <@{1}>'.format(user_id, user_id_2))

		if message.content.startswith('$add_credits'):
			if message.author.permissions_in(message.channel).administrator == False: await self.send_message(message.channel, '<@{}> sorry, but you are not allowed to perform this action'.format(user_id))
			else:
				user_id_2 = message.content[message.content.index('@')+1:message.content.index('>')]
				if (self.bank.get_account_info(user_id_2) == -1): 
					await self.send_message(message.channel, '<@{}> sorry, but the other user doesnt have bank account'.format(user_id))
				else:
					credits = message.content[message.content.index('!')+1:]
					if credits.isalpha(): await self.send_message(message.channel, '<@{}> sorry, credits are invalid'.format(user_id))
					else:
						if self.bank.add_credits(user_id_2, int(credits)) != -1: await self.send_message(message.channel, '<@{0}> you successfully transfered credits to <@{1}>'.format(user_id, user_id_2))

		if message.content.startswith('$help'):
			await self.send_message(message.channel, "BankBot created by pygh0st (2017 license GNU/GPL3.0)")

BOT_TOKEN = ''
BANK_FILE = 'bank.db'

client = BankBot(BANK_FILE)
client.run(BOT_TOKEN)

