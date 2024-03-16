import telebot
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

TOKEN = "7070202629:AAFQcYBicTkBmuzuhk7pyViV0LTkgR3E9RM"
rpc_user = 'kzcashrpc'
rpc_password = 'VxYnZE0pijltpc6PmIEjEzxk'
rpc_connection = AuthServiceProxy(f'http://{rpc_user}:{rpc_password}@127.0.0.1:8276')

bot_token = TOKEN
bot = telebot.TeleBot(bot_token)

def address_balance(args):
    inputs = rpc_connection.listunspent(0, 9999, args)
    balance = 0
    for input_data in inputs:
        balance += input_data.get("amount")
    return balance

@bot.message_handler(commands=['getnewaddress'])
def get_new_address(message):
    new_address = rpc_connection.getnewaddress()
    bot.reply_to(message, f"New address: {new_address}")

@bot.message_handler(commands=['getbalance'])
def get_balance(message):
    balance = rpc_connection.getbalance()
    bot.reply_to(message, f"Total wallet balance: {balance}")

@bot.message_handler(commands=['send'])
def send_coins(message):
    args = message.text.split()[1:]
    if len(args) != 3:
        bot.reply_to(message, "Template: /send <sender address> <recipient address> <amount>")
        return
    
    sender_address, receiver_address, amount = args
    
    try:
        inputs = rpc_connection.listunspent(0, 9999, [sender_address])
    except JSONRPCException:
        bot.reply_to(message, f"Invalid sender wallet address")
        return
    
    for input_data in inputs:
        if float(input_data.get("amount")) > (float(amount) + 0.001):
            break
    else:
        bot.reply_to(message, "Insufficient funds")
        return
    
    fee = float(input_data.get("amount")) - float(amount) - 0.001
    input_for_transaction = {"txid": input_data.get("txid"), "vout": input_data.get("vout")}
    
    try:
        create_transaction = rpc_connection.createrawtransaction([input_for_transaction], {receiver_address: amount, sender_address: fee})
        sign_transaction = rpc_connection.signrawtransaction(create_transaction)
        received_hex = sign_transaction.get("hex")
        txid = rpc_connection.sendrawtransaction(received_hex)
        bot.reply_to(message, f"Coins are sent to the recipient! Transaction ID: {txid}")
    except JSONRPCException as e:
        bot.reply_to(message, f"Error sending coins: {e}")

@bot.message_handler(commands=['getaddressbalance'])
def get_address_balance(message):
    args = message.text.split()[1:]
    if len(args) != 1:
        bot.reply_to(message, "Template: /getaddressbalance <wallet address>")
        return
    
    try:
        balance = address_balance(args)
        bot.reply_to(message, f"Address balance: {balance} KZC")
    except JSONRPCException:
        bot.reply_to(message, f"Invalid wallet address")

@bot.message_handler(content_types=['text'])
def send_message(message):
    bot.send_message(message.chat.id, message.text)

if __name__ == '__main__':
    bot.infinity_polling()

