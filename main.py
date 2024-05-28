from pyrogram import Client , filters
from pyrogram.types import Message , InlineKeyboardMarkup, InlineKeyboardButton 
import pyromod
import sqlite3 as sq

#creating data base
db = sq.connect("data_users.db")
cursor = db.cursor()
db.execute(
    """CREATE TABLE IF NOT EXISTS users(
        id_db INTEGER PRIMARY KEY,
        id_tel INTEGER,
        firstname VARCHAR(30),
        lastname VARCHAR(30),
        user_name VARCHAR(30),
        num_of_message INTEGER,
        group_id INTEGER,
        bank_acc_num INTEGER(20)
        )"""
)

db.commit()



#defaults
learn_how_to_recive_id_group = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("آموزش پیدا کردن آیدی❓", callback_data="learn_how_to_recive_id_group")]
    ]
)

keyboard_main = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("من owner هستم", callback_data="im_owner")],
        [InlineKeyboardButton("من member هستم", callback_data="im_member")]
    ]
)

id_members_for_recive_receipt_in_callback_Query = []


# connecting to bot | fill
api_id = 1111111
api_hash = ""
token= ""

app = Client("robot", api_id, api_hash, bot_token=token)

#recive messages from groups
@app.on_message(filters.group)
async def recive_msg_from_group(c:Client, m:Message):

    #check id in database
    def check_id_in_database():
        cursor.execute("SELECT id_tel FROM users WHERE id_tel=?", (m.from_user.id,))
        result = cursor.fetchone()
        if result:
            return True
        else:
            return False

    #add user to database
    def add_user_to_database():

        if check_id_in_database():
            pass
            return True
        else:
            db.execute(
                """
                INSERT INTO users(id_tel, firstname, lastname, user_name, num_of_message, group_id, bank_acc_num) VALUES(?,?,?,?,?,?,?)""",
                (m.from_user.id, m.from_user.first_name, m.from_user.last_name, m.from_user.username, 1, m.chat.id, 0)
            )
            db.commit()
            return False
        
    #add one message to database
    def add_one_message_to_database():
        if add_user_to_database():
            num_of_message = cursor.execute(
                """SELECT num_of_message FROM users"""
            )
            for i in num_of_message:
                num_of_message = i[0]   #recive num_of_message and save in num_of_message

            cursor.execute(
                "UPDATE users SET num_of_message=? WHERE id_tel =? ",(num_of_message+1, m.from_user.id)
            )
            db.commit()
        else:
            pass

    add_one_message_to_database() #adding message

    #Show the number of messages to the user
    if m.text == "myinfo": 

        num_of_message = cursor.execute(
            """SELECT num_of_message FROM users"""
        )
        for i in num_of_message:
            num_of_message = i[0]   #recive num_of_message and save in num_of_message

        await app.send_message(m.chat.id, "تعداد پیام های شما: **{}**".format(num_of_message), reply_to_message_id=m.id)

    if m.text == "IdGroup":
        await app.send_message(m.chat.id, "`{}`".format(m.chat.id))


@app.on_message(filters.private)
async def private(c:Client, m:Message):
    #Start the robot
    if m.text == "/start":

        await app.send_message(m.chat.id, "سلام به ربات خوش آمدید🎉. \nلطفا نقش خود را انتخاب نمایید.", reply_markup=keyboard_main)

#Receive queries
@app.on_callback_query()
async def query1(Client, call1):

    async def get_chat_member_status():     #get chat member status in group
        try:
            status_member = await app.get_chat_member(answer,call1.from_user.id)
            status_member = str(status_member.status)
            status_member = status_member.split(".")[1]
            return(status_member)
        except:
            status_member = "negative"
            return(status_member)

    data = call1.data

    #This query is for sending receipts to members
    for i in id_members_for_recive_receipt_in_callback_Query:
        if data == "send_receipt"+str(i):
            try:
                receipt = await app.ask(call1.message.chat.id,"رسید کارت به کارت را برای این کاربر ارسال کنید. \nزمان انتظار:**20ثانیه**",timeout=20)
                if receipt:
                    await app.send_photo(i, receipt.photo.file_id, caption ="✅رسید برای گروه با آیدی: `{}`\nتعداد پیام ها و درآمد شما ریست شد".format(id_members_for_recive_receipt_in_callback_Query[-1]))
                    cursor.execute(
                        """UPDATE users SET num_of_message =? WHERE id_tel =? AND group_id =?""",(0,i,id_members_for_recive_receipt_in_callback_Query[-1])
                    )
                    db.commit()
                    await app.send_message(call1.message.chat.id,"✅رسید ارسال شد و تعداد پیام های کاربر و درآمدش ریست شد!\nآیدی کاربر:**{}**".format(i))

            except:
                await app.send_message(call1.message.chat.id, "❌**رسید دریافت نشد!**")
    
    #This is a query for learning how to get an ID
    if data=="learn_how_to_recive_id_group":
        await app.send_message(call1.message.chat.id, "🆔**آموزش پیدا کردن آیدی عددی گروه** \n برای پیدا کردن آیدی عددی گروه ابتدا باید ربات را در گروه مد نظر اضافه کرده و در ادامه آن را ادمین کرده باشید. سپس در گروه عبارت `IdGroup` را ارسال کرده تا آیدی گروه به شما نمایش داده شود. \nسپس ایدی را با منهای اولش برای ربات ارسال کنید.")


    #This is a query to get the ID of the group from the owner
    if data == "im_owner":

        try:
            answer = await app.ask(call1.message.chat.id, "لطفا آیدی عددی گروه مد نظر را ارسال نمایید. \n مدت زمان انتظار **30** ثانیه میباشد.", timeout=30, reply_markup=learn_how_to_recive_id_group)
            answer = int(answer.text)
            if answer:
                await app.send_message(call1.message.chat.id, "✅آیدی دریافت شد: \n{}".format(answer))

        except:
            await app.send_message(call1.message.chat.id, "❌**آیدی دریافت نشد!**")

        status_member = await get_chat_member_status() 
        users_are_in_group = []

        if status_member == "OWNER":    #Confirm the owner
            await app.send_message(call1.message.chat.id, "✅**تایید شد!** شما owner گروه هستید!")
            res = cursor.execute(
                "SELECT id_tel, firstname, lastname, user_name, num_of_message, bank_acc_num, group_id FROM users ORDER BY num_of_message DESC LIMIT 5"
            )
            for i in res :
                group_id = i[-1]
                if group_id == answer:
                    users_are_in_group.append(i[0:7])   #Get information from the database and add it to the list

            for i in users_are_in_group:
                firstname_person = i[1]
                lastname_person = i[2]
                NumOfMessage_person = i[4]
                money_person = str(NumOfMessage_person) + "تومان"
                BankAccNumber_person = i[5]
                UserName_person = i[3]
                IdTelegram_person = i[0]
                Id_group = i[6]

                id_members_for_recive_receipt_in_callback_Query.append(IdTelegram_person)   #Add the group ID to the end of the list

                keyboard_for_send_receipt = InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("ارسال رسید برای این کاربر", callback_data="send_receipt"+str(IdTelegram_person))],
                    ]
                )
                index_in_list= users_are_in_group.index(i) + 1
                await app.send_message(call1.message.chat.id, "**نفر{}ام**{} \nنام: {}\nنام خانواگی: {}\nتعداد پیام: {}\nهزینه: **{}** \nشماره حساب: `{}`\n \nیوزرنیم: @{}\nآیدی تلگرام: `{}`\nآیدی گروه: `{}`".format(index_in_list, "🏅", firstname_person, lastname_person, NumOfMessage_person, money_person, BankAccNumber_person, UserName_person, IdTelegram_person, Id_group),reply_markup=keyboard_for_send_receipt)
            
            id_members_for_recive_receipt_in_callback_Query.append(Id_group)

        else:
            await app.send_message(call1.message.chat.id, "❌**شما owner گروه نیستید!**")

        
        
    #This is a query to get an ID from a group member
    if data == "im_member" :

        try:
            answer = await app.ask(call1.message.chat.id, "لطفا آیدی عددی گروه مد نظر را ارسال نمایید. \n مدت زمان انتظار **30** ثانیه میباشد.", timeout=30, reply_markup=learn_how_to_recive_id_group)
            answer = int(answer.text)
            if answer:
                await app.send_message(call1.message.chat.id, "✅آیدی دریافت شد: \n{}".format(answer))

        except:
            await app.send_message(call1.message.chat.id, "❌**آیدی دریافت نشد!**")

        status_member = await get_chat_member_status()
        if status_member =="MEMBER" or "ADMINISTRATOR":
            await app.send_message(call1.message.chat.id, "✅شما member هستید!")
            result =cursor.execute("SELECT bank_acc_num FROM users WHERE id_tel ={}".format(int(call1.from_user.id)))

            for i in result:
                if i[0] == 0:
                    try:
                        #Get the bank account number and save it on the database
                        bank_acc_num = await app.ask(call1.message.chat.id,"💳هیچ شماره حسابی ست نشده است.\n شماره حساب خود را **بدون فاصله** ارسال نمایید.")
                        bank_acc_num = int(bank_acc_num.text)
                        if bank_acc_num:
                            cursor.execute(
                                "UPDATE users SET bank_acc_num=? WHERE id_tel =? ",(bank_acc_num, call1.from_user.id)
                            )
                            db.commit()

                            await app.send_message(call1.message.chat.id, "✅شماره حساب دریافت شد و در اطلاعات شما ست شد: \n{}\nربات را بلاک نکنید تا رسید ها را دریافت کنید.".format(bank_acc_num))
                    except:
                        await app.send_message(call1.message.chat.id, "❌شماره حساب دریافت نشد!")

                else:
                    await app.send_message(call1.message.chat.id, "شماره حساب شما از قبل ست شده است: \n`{}`".format(i[0]))

app.run()