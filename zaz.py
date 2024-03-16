import telebot
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

TOKEN = "7070202629:AAFQcYBicTkBmuzuhk7pyViV0LTkgR3E9RM"
rpc_user = 'kzcashrpc'
rpc_password = 'f4aQo96JINEqNyW1msoVUMt2'
rpc_connection = AuthServiceProxy(f'http://{rpc_user}:{rpc_password}@127.0.0.1:8276')

bot = telebot.TeleBot(TOKEN)

def address_balance(args):
    try:
        inputs = rpc_connection.listunspent(0, 9999, [args])
        balance = sum(input["amount"] for input in inputs)
        return balance
    except JSONRPCException as e:
        print(f"Error: {e}")
        return None

@bot.message_handler(commands=['getnewaddress'])
def get_new_address(message):
    try:
        new_address = rpc_connection.getnewaddress()
        bot.reply_to(message, f"New address: {new_address}")
    except JSONRPCException as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['getbalance'])
def get_balance(message):
    try:
        balance = rpc_connection.getbalance()
        bot.reply_to(message, f"Total wallet balance: {balance}")
    except JSONRPCException as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['send'])
def send_coins(message):
    args = message.text.split()[1:]
    if len(args) != 3:
        bot.reply_to(message, "Template: /send <sender address> <recipient address> <amount>")
        return

    sender_address, receiver_address, amount = args
    try:
        inputs = rpc_connection.listunspent(0, 9999, [sender_address])
        if not inputs:
            bot.reply_to(message, "Sender address has no unspent outputs")
            return

        total_amount = sum(input["amount"] for input in inputs)
        if total_amount < float(amount):
            bot.reply_to(message, "Insufficient funds")
            return

        outputs = {receiver_address: float(amount), sender_address: total_amount - float(amount) - 0.001}
        raw_transaction = rpc_connection.createrawtransaction(inputs, outputs)
        signed_transaction = rpc_connection.signrawtransaction(raw_transaction)
        txid = rpc_connection.sendrawtransaction(signed_transaction["hex"])
        bot.reply_to(message, f"Coins are sent to the recipient! Transaction ID: {txid}")
    except JSONRPCException as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['getaddressbalance'])
def get_address_balance(message):
    args = message.text.split()[1:]
    if len(args) != 1:
        bot.reply_to(message, "Template: /getaddressbalance <wallet address>")
        return

    balance = address_balance(args[0])
    if balance is not None:
        bot.reply_to(message, f"Address balance: {balance} KZC")
    else:
        bot.reply_to(message, "Error: Invalid wallet address")

@bot.message_handler(content_types=['text'])
def send_message(message):
    bot.send_message(message.chat.id, message.text)

if _name_ == '_main_':
    bot.infinity_polling()
