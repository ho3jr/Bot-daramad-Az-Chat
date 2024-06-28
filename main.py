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
        bank_acc_num INTEGER(20),
        status_for_bot VARCHAR(30)
        )"""
)

db.commit()



#defaults

you_are_ADMIN = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("آمار گروه", callback_data="Stats_of_Group")]
    ]
)


learn_how_to_recive_id_user = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("آموزش پیدا کردن آیدی❓", callback_data="learn_how_to_recive_id_User")]
    ]
)


you_are_OWNER = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("آمار گروه", callback_data="Stats_of_Group")],
        [InlineKeyboardButton("تنظیم مدیر برای ربات", callback_data="set_Admin")],
        [InlineKeyboardButton("لیست مدیران گروه", callback_data="list_Admins")]
    ]
)


learn_how_to_recive_id_group = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("آموزش پیدا کردن آیدی❓", callback_data="learn_how_to_recive_id_group")]
    ]
)

keyboard_main = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("من owner هستم", callback_data="im_owner")],
        [InlineKeyboardButton("من admin هستم", callback_data="im_admin")],
        [InlineKeyboardButton("من member هستم", callback_data="im_member")],
        [InlineKeyboardButton("راهنما و درباره ربات", callback_data="help")]
    ]
)

keyboard_member_what_do = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("آمار من در گروه", callback_data="my_stats")],
        [InlineKeyboardButton("شماره حساب", callback_data="my_bank_acc_num_management")]
    ]
)

id_members_for_recive_receipt_in_callback_Query = []
id_ADMINs_for_Dismissal_in_callback_Query = []


# connecting to bot
api_id = 1111111
api_hash = "FILL HERE"
token= "FILL HERE"

app = Client("robot", api_id, api_hash, bot_token=token)



#recive messages from groups
@app.on_message(filters.group)
async def recive_msg_from_group(c:Client, m:Message):

    async def get_chat_member_status():     #get chat member status in group
        try:
            status_member = await app.get_chat_member(m.chat.id,m.from_user.id)
            status_member = str(status_member.status)
            status_member = status_member.split(".")[1]
            return(status_member)
        except:
            status_member = "negative"
            return(status_member)

    #check id in database
    def check_id_in_database():
        cursor.execute("SELECT id_tel FROM users WHERE id_tel=?", (m.from_user.id,))
        result = cursor.fetchone()
        if result:
            return True

    #add user to database
    async def add_user_to_database(): 

        status_member = await get_chat_member_status()

        if status_member != "OWNER":
            if check_id_in_database():
                pass
                return True
            else:
                db.execute(
                    """
                    INSERT INTO users(id_tel, firstname, lastname, user_name, num_of_message, group_id, bank_acc_num, status_for_bot) VALUES(?,?,?,?,?,?,?,?)""",
                    (m.from_user.id, m.from_user.first_name, m.from_user.last_name, m.from_user.username, 1, m.chat.id, 0, "MEMBER")
                )
                db.commit()
                return False
            
        if status_member == "OWNER":
            if check_id_in_database():
                pass
                return True
            else:
                db.execute(
                    """
                    INSERT INTO users(id_tel, firstname, lastname, user_name, num_of_message, group_id, bank_acc_num, status_for_bot) VALUES(?,?,?,?,?,?,?,?)""",
                    (m.from_user.id, m.from_user.first_name, m.from_user.last_name, m.from_user.username, 1, m.chat.id, 0, "OWNER")
                )
                db.commit()
                return False
            
        
    #add one message to database
    async def add_one_message_to_database(): 
        if await add_user_to_database():
            num_of_message = cursor.execute(
                """SELECT num_of_message FROM users"""
            )
            for i in num_of_message:
                num_of_message = i[0]   #recive num_of_message and save in num_of_message
                num_of_message = int(num_of_message)

            cursor.execute(
                "UPDATE users SET num_of_message=? WHERE id_tel =? ",(num_of_message+1, m.from_user.id)
            )
            db.commit()
        else:
            pass

    await add_one_message_to_database() #adding message

    #Show the number of messages to the user
    if m.text == "myinfo": 

        num_of_message = cursor.execute(
            """SELECT num_of_message FROM users"""
        )
        for i in num_of_message:
            num_of_message = i[0]   #recive num_of_message and save in num_of_message

        await app.send_message(m.chat.id, "تعداد پیام های شما: **{}**".format(num_of_message), reply_to_message_id=m.id)

    if m.text == "IdGroup":     #send ID group
        await app.send_message(m.chat.id, "`{}`".format(m.chat.id))

    if m.text == "ranking":     #send stats to group
        status_member = await get_chat_member_status()
        if status_member == "OWNER" or status_member == "ADMINISTRATOR":
            users_are_in_group = []
            res = cursor.execute(
                "SELECT id_tel, firstname, lastname, user_name, num_of_message, bank_acc_num, group_id FROM users ORDER BY num_of_message DESC LIMIT 5"
            )
            for i in res :
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

                index_in_list= users_are_in_group.index(i) + 1
                text = "**نفر{}ام**{} \nنام: {}\nنام خانواگی: {}\nتعداد پیام: {}\nهزینه: **{}** \nشماره حساب: `{}`\n \nیوزرنیم: @{}\nآیدی تلگرام: `{}`\nآیدی گروه: `{}`".format(index_in_list, "🏅", firstname_person, lastname_person, NumOfMessage_person, money_person, BankAccNumber_person, UserName_person, IdTelegram_person, Id_group)
                await app.send_message(m.chat.id, text)

    if m.text == "id":      #send UserID in Group
        try:
            userID = m.reply_to_message.from_user.id
            await app.send_message(m.chat.id, "`{}`".format(userID),reply_to_message_id= m.id)
        except:
            pass

@app.on_message(filters.private)
async def private(c:Client, m:Message):

    #Start the robot
    if m.text == "/start":

        await app.send_message(m.chat.id, "سلام به ربات خوش آمدید🎉. \nلطفا نقش خود را انتخاب نمایید.", reply_markup=keyboard_main)

#Receive queries
@app.on_callback_query()
async def query1(Client, call1):
    answer = 0
    data = call1.data

    async def get_chat_member_status():     #get chat member status in group
        try:
            status_member = await app.get_chat_member(answer,call1.from_user.id)
            status_member = str(status_member.status)
            status_member = status_member.split(".")[1]
            return(status_member)
        except:
            status_member = "negative"
            return(status_member)

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
                    id_members_for_recive_receipt_in_callback_Query.remove(i)
                    break
            except:
                await app.send_message(call1.message.chat.id, "❌**رسید دریافت نشد!**")
    
    #This is a query for learning how to get an ID
    if data=="learn_how_to_recive_id_group":
        await app.send_message(call1.message.chat.id, "🆔**آموزش پیدا کردن آیدی عددی گروه** \n برای پیدا کردن آیدی عددی گروه ابتدا باید ربات را در گروه مد نظر اضافه کرده و در ادامه آن را ادمین کرده باشید. سپس در گروه عبارت `IdGroup` را ارسال کرده تا آیدی گروه به شما نمایش داده شود. \nسپس ایدی را با منهای اولش برای ربات ارسال کنید.")

    if data =="im_admin":       #send ADMIN panel
        try:
            answer = await app.ask(call1.message.chat.id, "لطفا آیدی عددی گروه مد نظر را ارسال نمایید. \n مدت زمان انتظار **30** ثانیه میباشد.", timeout=30, reply_markup=learn_how_to_recive_id_group)
            answer = int(answer.text)
            if answer:
                await app.send_message(call1.message.chat.id, "✅آیدی دریافت شد: \n{}".format(answer))
                res=cursor.execute("SELECT status_for_bot FROM users WHERE id_tel ={} AND group_id = {}".format(int(call1.from_user.id), answer))

                for i in res:
                    if i[0] == "ADMIN":
                        await app.send_message(call1.message.chat.id,"✅**تایید شد!** شما admin ربات هستید!\nچه کاری براتون انجام بدم؟ ", reply_markup= you_are_ADMIN)
        except:
            await app.send_message(call1.message.chat.id, "❌**آیدی دریافت نشد!**")

    #This is a query to get the ID of the group from the owner
    if data == "im_owner":      #send OWNER panel

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
            await app.send_message(call1.message.chat.id, "✅**تایید شد!** شما owner گروه هستید!\nچه کاری براتون انجام بدم؟ ",reply_markup= you_are_OWNER)
        else:
            await app.send_message(call1.message.chat.id, "❌**شما owner گروه نیستید!**")

        
    #This is a query to get an ID from a group member
    if data == "im_member" :
        status_member = await get_chat_member_status()
        try:
            answer = await app.ask(call1.message.chat.id, "لطفا آیدی عددی گروه مد نظر را ارسال نمایید. \n مدت زمان انتظار **30** ثانیه میباشد.", timeout=30, reply_markup=learn_how_to_recive_id_group)
            answer = int(answer.text)
            if answer:
                await app.send_message(call1.message.chat.id, "✅آیدی دریافت شد: \n{}".format(answer))
                status_member = await get_chat_member_status()
                if status_member =="MEMBER" or status_member == "ADMINISTRATOR":
                    await app.send_message(call1.message.chat.id, "✅شما member هستید! \nچه کاری براتون انجام بدم؟", reply_markup= keyboard_member_what_do)
    
        except:
            await app.send_message(call1.message.chat.id, "❌**آیدی دریافت نشد!**")


    if data == "my_stats":  #Send user information
        status_member = get_chat_member_status()
        if status_member == "MEMBER" or status_member == "ADMINISTRATOR":
            User_information = []
            res = cursor.execute(
                    "SELECT id_tel, firstname, lastname, user_name, num_of_message, bank_acc_num FROM users WHERE id_tel ={}".format(int(call1.from_user.id))
                )
            for i in res :
                firstname_person = i[1]
                lastname_person = i[2]
                NumOfMessage_person = i[4]
                money_person = str(NumOfMessage_person) + "تومان"
                BankAccNumber_person = i[5]
                UserName_person = i[3]
                IdTelegram_person = i[0]
                User_information.append(i[0:6])

            text = "نام: {}\nنام خانوادگی:{}\nآیدی تلگرام:{}\nتعداد پیام:{}\nشماره حساب:{}\nدرآمد:{}".format(firstname_person, lastname_person, IdTelegram_person, NumOfMessage_person, BankAccNumber_person, money_person)
            await app.send_message(call1.message.chat.id,text)

    if data == "my_bank_acc_num_management":    #bank acc num management for member

        result =cursor.execute("SELECT bank_acc_num FROM users WHERE id_tel ={}".format(int(call1.from_user.id)))

        for i in result:
            if i[0] == 0:
                try:
                    #Get the bank account number and save it on the database
                    bank_acc_num = await app.ask(call1.message.chat.id,"💳هیچ شماره حسابی ست نشده است.\n شماره حساب خود را **بدون فاصله و به انگلیسی** ارسال نمایید.")
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

    if data == "help":  #send help
        await app.send_message(call1.message.chat.id, "سلام دوست عزیز\n\nاین ربات توسط [آية الطبيعة](https://t.me/NaGHiZam) نوشته شده است. این ربات جهت تشویق کاربران به فعالیت بیشتر نوشته شده است؛ با این سیاست که: پولی که برای تبلیغ در چنل های دیگران خرج میشود را میتوان بین کاربران پخش کرد. با این کار کاربران تعامل بیشتری با گروه برقرار میکنند و باعث رشد گروه میشود. حتی در آینده میتوانید چنلی را به گروه متصل کنید تا  کاربران بیشتری آن را ببینند. \n\nفرض کنید شما میخواهید تبلیغی را برای گروه یا چنل خود بخرید. برای این کار شما چند صد هزار تومن بودجه نیاز دارید تا به ادمین چنلی که قصد تبلیغ کردن در آن را دارید بدهید تا گروه یا چنل شما را تبلیغ کند. اگر ما همین مقدار پول را میان کاربران پخش کنیم چه؟ تعامل بیشتری برقرار نمیشود؟ این ربات دقیقا این کار را برای شما انجام میدهد. با هر یک عدد پیام مبلغی به شما افزوده میشود تا در انتها ادمین ها درآمد شما را به شما پرداخت کنند. \n\nحال ممکن است این سوال پدید بیاید که اگر ادمین ها درآمد من را پرداخت نکردند چه؟ خب این اعتبار ادمین و گروه را به شدت پایین میاورد تا جایی که کسی دیگر حاضر نیست در گروه فعالیت داشته باشد. پس ادمینی که قصدش رشد در تلگرام است هیچگاه اعتبار خودش را با عصبانیت و خشم ممبر هایی که از بدقولی به دست آمده عوض نمکیند. \n**توجه! ربات را در یک گروه اجرا کنید تا به مشکل نخورید!**\n  دستورات گروه:\n`IdGroup`  آیدی گروه\n`myinfo`  آمار شما در گروه\n`ranking`  رتبه بندی گروه\n`id`  با ریپلای زدن روی شخص آیدی آن دیده میشود",disable_web_page_preview=True)



    if data == "Stats_of_Group":    #request owner to send stats
        await app.delete_messages(call1.message.chat.id, call1.message.id)
        Id_group = 0
        users_are_in_group = []
        res = cursor.execute(
            "SELECT id_tel, firstname, lastname, user_name, num_of_message, bank_acc_num, group_id FROM users ORDER BY num_of_message DESC LIMIT 5"
        )
        for i in res :
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

    if data == "set_Admin":     #set ADMIN by OWNER AND save in DataBase
        await app.delete_messages(call1.message.chat.id, call1.message.id)
        try:
            answer = await app.ask(call1.message.chat.id, "آیدی عددی کاربری که قصد دارید در ربات ادمین شود را ارسال کنید.\nزمان ارسال: 30ثانیه ", timeout=30, reply_markup= learn_how_to_recive_id_user)
            if answer:
                answer = int(answer.text)
                cursor.execute(
                    "UPDATE users SET status_for_bot=? WHERE id_tel =? ",("ADMIN", answer)
                )
                db.commit()
                await app.send_message(call1.message.chat.id, "**✅با موفقیت ست شد!**")
        except:
            await app.send_message(call1.message.chat.id, "**❌خطا رخ داد!**")


    if data == "list_Admins":       #send list of ADMINs for OWNER
        ADMINs = []
        res = cursor.execute(
                "SELECT id_tel, firstname, lastname FROM users WHERE status_for_bot=?",("ADMIN",)
            )
        for i in res:
            ADMINs.append(i[0:3])

        for i in ADMINs:
            ADMIN_id = i[0]
            ADMIN_first_name = i [1]
            ADMIN_last_name = i [2]

            id_ADMINs_for_Dismissal_in_callback_Query.append(ADMIN_id)

            keyboard_for_Dismissal = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("عزل مقام این ادمین", callback_data="Dismissal"+str(ADMIN_id))],
                ]
            )
            index_in_list= ADMINs.index(i) + 1
            await app.send_message(call1.message.chat.id, "نام: {}\nنام خانوادگی: {}\nآیدی عددی: `{}`".format(ADMIN_first_name, ADMIN_last_name, ADMIN_id), reply_markup= keyboard_for_Dismissal)

    for i in id_ADMINs_for_Dismissal_in_callback_Query:
        if data == "Dismissal"+str(i):
            cursor.execute(
                "UPDATE users SET status_for_bot=? WHERE id_tel =? ",("MEMBER", i)
            )
            db.commit()
            await app.send_message(call1.message.chat.id,"✅کاربر با آیدی `{}` عزل مقام شد!".format(i))
            id_ADMINs_for_Dismissal_in_callback_Query.remove(i)
            break
    if data == "learn_how_to_recive_id_User":
        await app.send_message(call1.message.chat.id, "🆔**آموزش پیدا کردن آیدی عددی کاربر** \n برای پیدا کردن آیدی عددی کاربر ابتدا باید ربات را در گروه مد نظر اضافه کرده و در ادامه آن را ادمین کرده باشید. سپس بر روی کاربر ریپلای بزنید و عبارت `id` را ارسال کرده تا آیدی شخص به شما نمایش داده شود. \nسپس ایدی را برای ربات ارسال کنید.")



app.run()