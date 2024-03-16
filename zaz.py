import telebot
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
TOKEN = "7070202629:AAFQcYBicTkBmuzuhk7pyViV0LTkgR3E9RM"
rpc_user = 'kzcashrpc'
rpc_password = 'f4aQo96JINEqNyW1msoVUMt2'
rpc_connection = AuthServiceProxy(f'http://{rpc_user}:{rpc_password}@127.0.0.1:8276')
bot_token = TOKEN
bot = telebot.TeleBot(bot_token)
def addressBalance(args):
     inputs = rpc_connection.listunspent(0, 9999, args)
     balance = 0
     if len(inputs) == 0:
          balance += 0
     elif len(inputs) == 1:
          balance += inputs[0].get("amount")
     else:
         for i in (0, len(inputs)-1):
              balance += inputs[i].get("amount")
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
     for i in (0, len(inputs) - 1):
          temp = inputs[i]
          if float(float(temp.get("amount"))) > (float(amount)+0.001):
          break
          bot.reply_to(message, "Insufficient funds")
     return
         fee = float(temp.get("amount")) - float(amount) - 0.001
         inputForTransaction = {"txid":temp.get("txid"), "vout": temp.get("vout")}
     try:
        createTransaction = rpc_connection.createrawtransaction([inputForTransaction], {receiver_address:amount, sender_address:fee})
     except JSONRPCException:
          bot.reply_to(message, f"Invalid recipient wallet address")
     return
         signTransaction = rpc_connection.signrawtransaction(createTransaction)
         receivedHex = signTransaction.get("hex")
         txid = rpc_connection.sendrawtransaction(receivedHex)
         bot.reply_to(message, f"Coins are sent to the recipient! Transaction ID: {txid}")
@bot.message_handler(commands=['getaddressbalance'])
def get_address_balance(message):
      args = message.text.split()[1:]
      if len(args) != 1:
           bot.reply_to(message, "Template: /getaddressbalance <wallet address>")
      return 
      try:
         balance = addressBalance(args)
      except JSONRPCException:
         bot.reply_to(message, f"Invalid wallet address ")
      return
         bot.reply_to(message, f"Address balance: {balance} KZC")
@bot.message_handler(content_types=['text'])
def send_message(message):
     bot.send_message(message.chat.id, message.text)
     if name == '__main__':
         bot.infinity_polling()
