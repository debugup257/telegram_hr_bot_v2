import pandas as pd
import numpy as np
from ml_models import nlp
import yaml
import random
import os
import telebot
from db import GlobalVar
from telebot.types import InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
bot = telebot.TeleBot("5896087941:AAFpFb9ZEQ_omGXc7AC_PqsIxT6FZPRMZ2o")
db = GlobalVar("tiny.db.elephantsql.com", "ljbdoibm", "ljbdoibm", "TQeeYTeq6MXBw1EAnyW-7MrRwK4Qugk7")

names_df=pd.read_csv("all_names.csv")

nlp=nlp()
intent_df=nlp.raw_data_import("data\intent_detection.csv")
vocab_list=nlp.create_vocab()
intent_vector=nlp.create_tfidf("data\intent_detection.csv")
intent_tok=nlp.tokenize_intents(intent_df["intent"])
intent_y=nlp.output_series(intent_df,intent_tok)
nlp.naive_bayes_fit(intent_vector,intent_y)
intent_tok_reverse=nlp.invert_dict(intent_tok)

jd=nlp.read_yaml("jd.yaml")
basic_questions=nlp.read_yaml("basic_questions.yaml")
technical_questions=nlp.read_yaml("technical_questions.yaml")
technical_answers=nlp.read_yaml("technical_answers.yaml")
last_intent=None

roles=[i for i in jd["role"]]
roles_sent=",".join(roles)

users_state={}

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.chat.id
    users_state[uid] = {"tracker":0,"name":None,"email": None, "pan":None, "location":None, "exp":None, "edu":None, "eligible_roles":[],"shuffled_list":[],"final_basic_questions":[],"asked_questions":[],"technical":{}}
    for i in basic_questions:
        users_state[uid]["final_basic_questions"].append(random.choice(basic_questions[i]))



@bot.message_handler(func=lambda msg:True)
def introduction(message,nlp=nlp,users_state=users_state,db=db):
    uid=message.chat.id
    chat_id=message.chat.id
    user_reply = str(message.text).lower()
    reply_intent = intent_tok_reverse[nlp.naive_bayes_predict(nlp.vectorize(user_reply))]
    if users_state[uid]["tracker"]==0:
        if reply_intent == "greet":
            users_state[uid]["tracker"]=1
            print(users_state)
            return bot.send_message(chat_id, f'Hey there! I am Akshay from Innova Solutions. We are currently hiring .Would you like to take an interview ?')
   
    if users_state[uid]["tracker"]==1:   
        print(reply_intent)
        if reply_intent == "agree":
            users_state[uid]["tracker"]+=1
            print(users_state)
            if len(users_state[uid]["final_basic_questions"])>0:
                users_state[uid]["asked_questions"].append(users_state[uid]["final_basic_questions"][0])
                return bot.send_message(message.chat.id,users_state[uid]["final_basic_questions"].pop(0))
        if reply_intent== "disagree":
            return bot.reply_to(message, "Thank you, see you next time")
        else :
            return bot.reply_to(message, "I am portraying myself as a person, but actually I am a bot, can you please tell me clearly if you want to give the interview ? You will surely save you time if you clearly tell me !!!!")

    if users_state[uid]["tracker"]==2:
        print(user_reply)
        users_state[uid]["name"]=nlp.identify_name(user_reply, names_df)
        print(users_state[uid]["name"])
        if users_state[uid]["name"]!=None:
            users_state[uid]["tracker"]+=1
            if len(users_state[uid]["final_basic_questions"])>0:
                users_state[uid]["asked_questions"].append(users_state[uid]["final_basic_questions"][0])
                return bot.send_message(message.chat.id,users_state[uid]["final_basic_questions"].pop(0))
        if users_state[uid]["name"]==None:
                return bot.reply_to(message,f'Sorry, i think there has been a misunderstanding my question was "{users_state[uid]["asked_questions"][-1]}"')

    if users_state[uid]["tracker"]==3:
        print(user_reply)
        users_state[uid]["email"]=nlp.check_mail(user_reply)
        print(users_state[uid]["email"])
        if users_state[uid]["email"]!=None:
            print(users_state[uid]["email"])
            users_state[uid]["tracker"]+=1
            if len(users_state[uid]["final_basic_questions"])>0:
                users_state[uid]["asked_questions"].append(users_state[uid]["final_basic_questions"][0])
                return bot.send_message(message.chat.id,users_state[uid]["final_basic_questions"].pop(0))
        if users_state[uid]["email"]==None:
                return bot.reply_to(message,f'Sorry, i think there has been a misunderstanding my question was "{users_state[uid]["asked_questions"][-1]}"')

    if users_state[uid]["tracker"]==4:
        print(user_reply,"130")
        users_state[uid]["pan"]=nlp.identify_pan(user_reply)
        print(users_state[uid]["pan"],"after identification")
        if users_state[uid]["pan"]!=None:
            print(users_state[uid]["pan"],"if users_state[uid]")
            users_state[uid]["tracker"]+=1
            if len(users_state[uid]["final_basic_questions"])>0:
                users_state[uid]["asked_questions"].append(users_state[uid]["final_basic_questions"][0])
                return bot.reply_to(message,users_state[uid]["final_basic_questions"].pop(0))
        if users_state[uid]["pan"]==None:
                return bot.reply_to(message,f'Sorry, i think there has been a misunderstanding my question was "{users_state[uid]["asked_questions"][-1]}"')

    if users_state[uid]["tracker"]==5:
        print(user_reply)
        users_state[uid]["location"]=(user_reply)
        print(users_state[uid]["location"])
        if users_state[uid]["location"]!=None:
            print(users_state[uid]["location"])
            users_state[uid]["tracker"]+=1
            if len(users_state[uid]["final_basic_questions"])>0:
                users_state[uid]["asked_questions"].append(users_state[uid]["final_basic_questions"][0])
                return bot.reply_to(message,users_state[uid]["final_basic_questions"].pop(0))        
        if users_state[uid]["location"]==None:
                return bot.reply_to(message,f'Sorry, i think there has been a misunderstanding my question was "{users_state[uid]["asked_questions"][-1]}"')


    if users_state[uid]["tracker"]==6:
        print(user_reply)
        users_state[uid]["exp"]=nlp.identify_number(user_reply)
        print(users_state[uid]["exp"])
        if users_state[uid]["exp"]!=None:
            print(users_state[uid]["exp"])
            for i in jd["role"]:
                if int(users_state[uid]["exp"])>=int(jd["role"][i]["exp"]):
                    users_state[uid]["eligible_roles"].append(i)
            users_state[uid]["tracker"]+=1
            keyboard = InlineKeyboardMarkup()
            for label in users_state[uid]["eligible_roles"]:
                button = InlineKeyboardButton(label, callback_data=label)
                keyboard.add(button)
            return bot.reply_to(message, "I think you will be eligible for one of the follwoing: ", reply_markup=keyboard )

        if users_state[uid]["exp"]==None:
                return bot.reply_to(message,f'Sorry, i think there has been a misunderstanding my question was "{users_state[uid]["asked_questions"][-1]}"')
   
    if users_state[uid]["tracker"]==8:
        users_state[uid]["technical"][users_state[uid]["asked_questions"][-1]]=str(user_reply)
        if len(users_state[uid]["shuffled_list"])>0:
            question=users_state[uid]["shuffled_list"].pop(0)
            users_state[uid]["asked_questions"].append(question)
            return bot.send_message(message.chat.id, question )
        else:
            users_state[uid]["tracker"]+=2

            # uploading the data 
            available_id_in_db=list(db.fetch_column("id"))
            if uid in available_id_in_db:
                 uid=uid+1000000000
            db.insert_applicant(users_state[uid],uid)
            db.upload_data(users_state[uid]["technical"],uid)

            return bot.send_message(message.chat.id, "It was great talking to you, I will share your details to the hr and get back to you once the interview is evaluated" )




@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    uid=call.message.chat.id
    print("call_back")
    users_state[uid]["shuffled_list"] = random.sample(technical_questions[call.data], 4)
    if len(users_state[uid]["shuffled_list"])>0:
        question=users_state[uid]["shuffled_list"].pop(0)
        users_state[uid]["asked_questions"].append(question)
        bot.send_message(call.message.chat.id, question )
        users_state[uid]["tracker"]+=1


        
bot.infinity_polling()

