# pip install google-generativeai
# pip install deep_translator
import google.generativeai as genai
from flask import Flask, request, jsonify
from deep_translator import GoogleTranslator
import re
import json
from persian import convert_en_characters

app = Flask(__name__)
genai.configure(api_key="AIzaSyA7xCgGMZWorZ8JZmYm6AOsPiXq0-0Mutg")#"AIzaSyAkQIyuH8ig3e5TC6WoWoDkC3DJVTgvud0")


supportedModels = ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"]


def ReplaceNumbersPersian(txt):
    txt = txt.replace("۹", "8")
    txt = txt.replace("۷", "7")
    txt = txt.replace("۶", "6")
    txt = txt.replace("۵", "5")
    txt = txt.replace("۴", "4")
    txt = txt.replace("۳", "3")
    txt = txt.replace("۲", "2")
    txt = txt.replace("۱", "1")
    txt = txt.replace("۰", "0")
    return txt


@app.route("/darsyar/completions", methods=["POST"])
def chat_completion():
    model = request.json["model"]
    if model not in supportedModels:
        models = ", ".join(supportedModels)
        return f"Model not found, current models: {models}"
    tempature = request.json["tempature"]
    if isinstance(tempature, (int, float)) == False:
        return "tempature must be a number"
    if (0 <= tempature and tempature <= 1) == False:
        return "tempature must be between 0 and 1"
    question = ReplaceNumbersPersian(request.json["question"])
    realAnswer = ReplaceNumbersPersian(request.json["realAnswer"])
    userAnswer = ReplaceNumbersPersian(request.json["userAnswer"])

    if (
        has_non_english_words(question) == True
        or has_non_english_words(realAnswer) == True
        or has_non_english_words(userAnswer) == True
    ):
        question = translate("auto", "en", question)
        realAnswer = translate("auto", "en", realAnswer)
        userAnswer = translate("auto", "en", userAnswer)

    generation_config = {
        "temperature": 2,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "application/json",
    }

    # acceptable = gemini-1.5-pro, gemini-1.5-flash
    model = genai.GenerativeModel(
        model_name=model,
        generation_config=generation_config,
        system_instruction="You will be given the real answer of a question, alongside the answer of the user. Give a grade out of 5, then give feedback to the user in second person prespective.",
    )

    response = model.generate_content(
        [
            "You will be given the real answer of a question, alongside the answer of the user. Give a grade out of 5, then give feedback to the user. Don't be too hard. Don't give suggestions outside the real answer. If the user has said all the main points of the real answer, don't tell them to say anything else. Again, be easy on them and don't tell them to say something that isn't in the real answer. If they say more than the answer it's fine",
            "Question: What science is history?",
            "Real Answer: It is a science that studies various aspects of human life and past societies and examines and analyzes the causes and results of their thoughts and actions.",
            "User Answer: It is a science of old things",
            'output: {"grade": "0", "feedback": "You need to be more precise and give more examples"}',
            "Question: What is the purpose of history?",
            "Real Answer: Knowledge and awareness about the life of the past, which includes all intellectual, religious, political, military, economic, scientific aspects.",
            "User Answer: Knowledge and awareness about the life of the past",
            'output: {"grade": "2", "feedback": "You are correct, but you need to provide more examples"}',
            "Question: Write a description about Biston stone inscription",
            "Real Answer: (for study) The Bistoon stone inscription, which was carved on a mountain chest by the order of Darius I, the Achaemenid king, in the city of Bistoon, a function of Harsin city in the current Kermanshah province, is considered one of the largest stone inscriptions in the world. In this epitaph, Dariush has mentioned some of his actions, including suppressing Goumat Mog and... Dariush Shah says: This king who was born by Goumat Magh from Kamboja (son of Cyrus the Great) was in our (family) for a long time. That Geomat Mug took (it) from Cambodia. He captured Persia, Media, and other countries and made them his own. He became the king.. Then I with some men, that Geomat Magh and those who. The best men were his assistants, I killed... I took the king from him. By the will of Ahura Mazda, I became a king.",
            "User Answer: It is an old thing made by darius",
            'output: {"grade": "0.25", "feedback": "You need to be more specific and provide more details about the inscription. For example, you could mention where it is located, what it says, and why it is important."}',
            "Question: Write why the Biston stone inscription is considered as an authentic historical document?",
            "Real Answer: Because it has expressed a lot of information about the developments of that era.",
            "User Answer: Because it is real",
            'output: {"grade": "0", "feedback": "You need to be more specific and provide more details about why the inscription is considered authentic. For example, you could mention the language it is written in, the fact that it was written by a king, or the historical context in which it was created."}',
            "Question: What was the text of God Namek?",
            "Real Answer: There were books that contained the names and actions of ancient kings.",
            "User Answer: It talked about ancient kings",
            'output: {"grade": "3", "feedback": "You need to be more specific and provide more details about the text. For example, you could mention what kind of information it contained, what language it was written in, or where it was found."}',
            "Question: Write a description about the legendary history?",
            "Real Answer: Even before the invention of calligraphy, ancient tribes and societies paid attention and interest to the history of their predecessors. Therefore, the history of their people and community was usually passed on orally from the beginning of creation. These biographies were mixed with legends and epic stories, and later, when historiography began, parts of them entered historical books.",
            "User Answer: Ancient tribes and societies paid attention to the history of their predecessors. the history of their people was usually passed on orally from the beginning of creation. They were mixed with legends, and later, parts of them entered historical books.",
            'output: {"grade": "4", "feedback": "You are correct, it would be even better if you were more specific"}',
            "Question: How have the scientists separated science?",
            "Real Answer: Physics, Chemistry, Geology, Biology",
            "User Answer: They have separated science into physics, chemistry, geology, and biology",
            'output: {"grade": "5", "feedback": "You are correct"}',
            "Question: What is the relationship between centimeters and kilometers?",
            "Real Answer: Each centimeter is one hundred thousandth of a kilometer.",
            "User Answer: One centimeter is one hundred thousand kilometers.",
            'output: {"grade": "5", "feedback": "You are correct"}',
            "Question: Write a description about the old way of writing history?",
            "Real Answer: Until the 19th century Historians often focused on organizing, recording and writing events and did not pay much attention to investigating the causes, effects and results of historical events. Also, most of those historians focused on political and military events and biography of rulers and did not pay attention to social, economic and cultural issues.",
            "User Answer: Historians often focused on organizing and writing events and did not pay much attention to the causes and, results of events. Some historians focused on political and military, and rulers didn't care about social and economic and cultural issues.",
            'output: {"grade": "5", "feedback": "You are correct"}',
            "Question: Is python a programming language?",
            "Real Answer: True() False(✔️)",
            "User Answer: False",
            'output: {"grade": "5", "feedback": "You are correct"}',
            'Question: Explain the command "left, left".',
            f"Question: {question}",
            f"Real Answer: {realAnswer}",
            f"User Answer: {userAnswer}",
            "output: ",
        ]
    )

    responseJson = json.loads(response.text)

    responseJson["feedback"] = translate("auto", "fa", responseJson["feedback"])
    return jsonify(responseJson)


@app.route("/darsyar/hint", methods=["POST"])
def hint_request():
    model = request.json["model"]
    if model not in supportedModels:
        models = ", ".join(supportedModels)
        return f"Model not found, current models: {models}"
    tempature = request.json["tempature"]
    if isinstance(tempature, (int, float)) == False:
        return "tempature must be a number"
    if (0 <= tempature and tempature <= 1) == False:
        return "tempature must be between 0 and 1"
    question = ReplaceNumbersPersian(request.json["question"])
    answer = ReplaceNumbersPersian(request.json["answer"])

    generation_config = {
        "temperature": tempature,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    model = genai.GenerativeModel(
        model_name=model,
        generation_config=generation_config,
        # safety_settings = Adjust safety settings
        # See https://ai.google.dev/gemini-api/docs/safety-settings
    )

    question = translate("auto", "en", question)
    answer = translate("auto", "en", answer)

    response = model.generate_content(
        [
            "Give a hint to the user on how to get to the answer of the question. Don't be too vague but don't tell the answer as exactly. Giving a small part of the answer is welcome.",
            "Question What science is history?",
            "Answer It is a science that studies various aspects of human life and past societies and examines and analyzes the causes and results of their thoughts and actions.",
            "Hint Think about the *methodology* used by historians. What tools do they use to uncover and understand the past? What does it study? What does it examine?  Consider the ways in which history is similar to other scientific disciplines.",
            "Question Write a description about Biston stone inscription",
            "Answer (for study) The Bistoon stone inscription, which was carved on a mountain chest by the order of Darius I, the Achaemenid king, in the city of Bistoon, a function of Harsin city in the current Kermanshah province, is considered one of the largest stone inscriptions in the world. In this epitaph, Dariush has mentioned some of his actions, including suppressing Goumat Mog and... Dariush Shah says: This king who was born by Goumat Magh from Kamboja (son of Cyrus the Great) was in our (family) for a long time. That Geomat Mug took (it) from Cambodia. He captured Persia, Media, and other countries and made them his own. He became the king.. Then I with some men, that Geomat Magh and those who. The best men were his assistants, I killed... I took the king from him. By the will of Ahura Mazda, I became a king.",
            "Hint Think about the *purpose* of the inscription. Why did Darius I commission it? What message was he trying to convey to those who would see it? Consider the inscription's *language* and the *symbols* it uses. \n\nHere's a small tip: IIt's made by Darius |, and in the city of bistoon.",
            f"Question {question}",
            f"Answer {answer}",
            "Hint ",
        ]
    )

    return translate("auto", "fa", response.text)


@app.route("/darsyar/tutor", methods=["POST"])
def tutor():
    '''model = request.json["model"]
    if model not in supportedModels:
        models = ", ".join(supportedModels)
        return f"Model not found, current models: {models}"'''
    

    '''tempature = request.json["tempature"]
    if isinstance(tempature, (int, float)) == False:
        return "tempature must be a number"
    if (0 <= tempature and tempature <= 1) == False:
        return "tempature must be between 0 and 1"'''
    

    question = convert_en_characters(request.json["question"])

    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        # safety_settings = Adjust safety settings
        # See https://ai.google.dev/gemini-api/docs/safety-settings
    )

    question = translate("auto", "en", question)

    response = model.generate_content([
        "You are a tutor. Your name is Darsyar and the country you're in is Iran. You student asks you a question. Answer their question as if you're their tutor. You don't know the student's name",
        "input: " + question,
    ])

    return translate("auto", "fa", response.text)


def translate(source, target, text):
    translated = GoogleTranslator(source=source, target=target).translate(text)
    return translated.lower()


def has_non_english_words(text):
    non_english_pattern = re.compile(r"[^\x00-\x7F]+")
    return bool(non_english_pattern.search(text))

if __name__ == '__main__':
    app.run(debug=True)