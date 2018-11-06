from chalice import Chalice
import logging
import json
import random
import re
import os
import sys
import alexa_speech
import langs

app = Chalice(app_name='alexa-proglang')
logger = logging.getLogger()
debug = os.environ.get('DEBUG_MODE')
if debug == '1':
    logger.setLevel(logging.INFO)
else:
    logger.setLevel(logging.ERROR)

#mp3
drumrole_mp3 = "soundbank://soundlibrary/musical/amzn_sfx_drum_and_cymbal_01"

@app.lambda_function()
def default(event, context):
    request = event['request']
    request_type = request['type']
    session = {}

    if request_type == 'LaunchRequest':
        return questionIntent()
    elif request_type == 'IntentRequest' and 'intent' in request:
        if 'dialogState' in request and request['dialogState'] != 'COMPLETED': 
           logger.info('run DialogDelegate()')
           #return alexa_speech.DialogDelegate().build()
           return onDialogState(request, request['intent'], request['dialogState'])
        else:
           return in_intent(request, session)

def in_intent(request, session):
    intent = request['intent']
    logger.info(str(intent))

    if intent['name'] == 'questionIntent':
        return questionIntent()
    elif intent['name'] == 'AMAZON.HelpIntent':
        return helpIntent()
    elif intent['name'] == 'AMAZON.NavigateHomeIntent':
        return helpIntent()
    elif intent['name'] == 'AMAZON.StopIntent':
        return finishIntent()
    elif intent['name'] == 'AMAZON.CancelIntent':
        return finishIntent()
    elif intent['name'] == 'AMAZON.NoIntent':
        return finishIntent()
    else:
        return questionIntent()


def onDialogState(request, intent, dialogState):
    if dialogState == 'STARTED':
        return alexa_speech.DialogDelegate().build()
    if dialogState == 'IN_PROGRESS':
        if 'value' not in intent['slots']['emotionSlot']:
            return alexa_speech.DialogDelegate().build()
        elif 'value' not in intent['slots']['hopeSlot']:
            return alexa_speech.DialogDelegate().build()
        elif 'value' not in intent['slots']['statusSlot']:
            return alexa_speech.DialogDelegate().build()
        elif 'value' not in intent['slots']['weatherSlot']:
            return alexa_speech.DialogDelegate().build()
        elif 'value' not in intent['slots']['hangrySlot']:
            return alexa_speech.DialogDelegate().build()
        else:
            return answerIntent(request, intent, intent['slots'])

def finishIntent():
    return alexa_speech.OneSpeech(u'お役に立てなくて残念です。またチャレンジしてくださいね。さようなら').build()

def helpIntent():
    return alexa_speech.QuestionSpeech(u'あなたの今日の調子や気分から今日のプログラム言語を予想します。占いみたいなもんだと思ってください。５つの質問をするので１から５までの５段階の数字で答えてください。はじめますか？', False, '「はい」か「いいえ」で答えてください').build()

def questionIntent():
    return alexa_speech.QuestionSpeech(u'開発言語予報です。あなたの今日の調子や気分から今日のプログラム言語を予想します。占いみたいなもんだと思ってください。５つの質問をするので１から５までの５段階の数字で答えてください。準備はよろしいですか？', False, '「はい」か「いいえ」で答えてください').build()

def answerIntent(request, intent, slots):
    logger.info(str(slots))

    try:
        _sts = slots['statusSlot']['value']
        _hgy = slots['hangrySlot']['value']
        _hpe = slots['hopeSlot']['value']
        _emt = slots['emotionSlot']['value']
        _wtr = slots['wtrSlot']['value']
        _sts = 5 if int(_sts) > 5 else 1 if int(_sts) < 1 else int(_sts)
        _hgy = 5 if int(_hgy) > 5 else 1 if int(_hgy) < 1 else int(_hgy)
        _hpe = 5 if int(_hpe) > 5 else 1 if int(_hpe) < 1 else int(_hpe)
        _emt = 5 if int(_emt) > 5 else 1 if int(_emt) < 1 else int(_emt)
        _wtr = 5 if int(_wtr) > 5 else 1 if int(_wtr) < 1 else int(_wtr)
    except Exception as e:
        _sts = 1
        _hgy = 1
        _hpe = 1
        _emt = 1
        _wtr = 20


    score = {}
    for l in langs.lang:
       logger.info(str(l))
       logger.info(str(score))
       score[str(l['k'])] = int(l['p'][0]) * (6 - _sts) 
    for l in langs.lang:
       score[str(l['k'])] += int(l['p'][1]) * (6 - _hgy) 
    for l in langs.lang:
       score[str(l['k'])] += int(l['p'][2]) * _hpe
    for l in langs.lang:
       score[str(l['k'])] += int(l['p'][3]) * _emt 
    for l in langs.lang:
       score[str(l['k'])] += int(random.choice(range(1,10))) * (6 - _wtr)

    rnk = sorted(score.items(), key=lambda x: -x[1])
    logger.info(rnk)
    top = langs.lang[int(rnk[0][0])-1]
    snd = langs.lang[int(rnk[1][0])-1]
    thd = langs.lang[int(rnk[2][0])-1]

    ptn = random.choice(range(1,3))
    text = '今日のあなたのプログラミング言語は<break time="0.5s"/>'
    text += '<audio src="%s" />' % drumrole_mp3

    if ptn == 1:
        text += u'<prosody rate="105%"><prosody volume="+1dB">' + top['a'] + 'でしょう！</prosody></prosody>'
        text += top['a'] + 'は、<break time="0.5s" />' + top['i'] + 'ですね。'
        text += u'<break time="0.5s" />遊んでくれてありがとう。ではまた！'
    elif ptn == 2:
        text += u'<prosody rate="105%"><prosody volume="+1dB">' + top['a'] + '<break time="0.3s" />ときどき<break time="0.3s" />' + snd['a'] + 'でしょう！</prosody></prosody>'
        text += top['a'] + 'は、<break time="0.5s" />' + top['i'] + 'ですね。'
        text += u'<break time="0.5s" />遊んでくれてありがとう。ではまた！'
    else:
        text += u'<prosody rate="105%"><prosody volume="+1dB">' + top['a'] + '<break time="0.3s" />のち<break time="0.3s" />' + snd['a'] + 'で、'
        text += u'時折、' + thd['a'] + 'を伴うでしょう！</prosody></prosody>'
        text += top['a'] + 'は、<break time="0.5s" />' + top['i'] + 'ですね。'
        text += u'<break time="0.5s" />遊んでくれてありがとう。ではまた！'

    return alexa_speech.OneSpeech(text).build()
