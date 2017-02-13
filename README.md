# BankBot
A simple python discord bot using discordpy API (by Rapptz: https://github.com/Rapptz/discord.py). 

This bot create add a credit system (money system).

## Commands
All the commands start with a "$", this is the list of the implemented commands:

**$help**: list of commands

**$create_account**: create a bank account for the user entered the command (work only if the user doesn't have a bank account)

**$account_info**: show the user info (his ID and his credits)

**$transfer username !credits**: Transfer the amount of credits specified to the user specified (don't forget the "!" before the amount of credits)

**$add_credits username !credits**: Add the amount of credits to the user (work only for people who have administrator rights)

## How it works ?
The python script can only be runned with Python3.5+, he use *asyncio*, *discord* and *sqlite*.
All the data are writed to a file named **bank.db**, this file is a **sqlite** file. You need SQLite browser to edit it.

## Please report me any weaks or bug.


