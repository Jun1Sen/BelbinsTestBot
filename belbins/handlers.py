import re

from aiogram_dialog.widgets.kbd import Row, Button, Select
from aiogram_dialog.widgets.text import Const, Format, Jinja

from LoadData import data
from roles import roles_name

from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from dispatcher import dp


class StartSG(StatesGroup):
    start = State()
    window_chapter = State()
    window_answer_ball = State()
    window_conclusion = State()


async def some_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data.update(question_index="0", bank_of_ball="10")
    await dialog_manager.next()

async def reset_hndler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data.update(question_index="0", bank_of_ball="10")
    await dialog_manager.switch_to(StartSG.window_chapter)

async def chapter_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    all_questions = len(data)
    current_question = int(dialog_manager.dialog_data.get("question_index")) + 1
    if all_questions > current_question:
        dialog_manager.dialog_data.update(question_index = str(int(dialog_manager.dialog_data.get("question_index")) + 1), bank_of_ball = "10")
        await dialog_manager.switch_to(StartSG.window_chapter)
    else:
        await dialog_manager.switch_to(StartSG.window_conclusion)


async def answer_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, *args, **kwargs):
    match = re.search(r'\d+$', callback.data)
    if match:
        index_answer = match.group()
        dialog_manager.dialog_data.update(answer_index = str(int(index_answer) -1))
        await dialog_manager.switch_to(StartSG.window_answer_ball)


async def write_ball_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, *args, **kwargs):
    match = re.search(r'\d+$', callback.data)
    memory_data = dialog_manager.dialog_data
    if match:
        current_ball = int(match.group())

        question_index = int(memory_data.get("question_index"))
        answer_index = int(memory_data.get("answer_index"))
        bank = int(memory_data.get("bank_of_ball"))

        data_balls = {}
        if memory_data.get("data_balls") is not None:
            data_balls = memory_data.get("data_balls")
        else:
            data_balls = data

        old_ball = int(data_balls[question_index]["Answers"][answer_index]["ball"])
        new_bank = bank - current_ball + old_ball
        data_balls[question_index]["Answers"][answer_index]["ball"] = str(current_ball)
        dialog_manager.dialog_data.update(data_balls = data_balls)

        dialog_manager.dialog_data.update(bank_of_ball = str(new_bank))

        await dialog_manager.switch_to(StartSG.window_chapter)


async def answer_getter(**kwargs):
    dialog_manager = kwargs.get("dialog_manager")
    memory_data = dialog_manager.dialog_data
    index_question = int(memory_data.get("question_index"))
    index_answer = int(memory_data.get("answer_index"))
    balls = int(memory_data.get("bank_of_ball"))
    question = data[index_question]["Question"]
    answer = data[index_question]["Answers"][index_answer]["Answer"]
    select_ball = "Выберите балл, который вы хотите назначить ответу"
    rows = 2
    return {
        "text_question_answers": question + "\n\n" + answer +
        "\n\n" + select_ball,
        "balls_row1": [ball for ball in range(balls // rows + 1)],
        "balls_row2":[ball for ball in range(balls // rows + 1, balls + 1)]
    }


async def question_getter(**kwargs):
    dialog_manager = kwargs.get("dialog_manager")
    num_question = int(dialog_manager.dialog_data.get("question_index"))
    answers = data[num_question]["Answers"]
    question = data[num_question]["Question"]
    answers_str = "\n\n".join([str(index) + ". " + answer["Answer"] for answer, index in zip(answers, range(1, len(answers) + 1))])
    data_balls = dialog_manager.dialog_data.get("data_balls")
    balls = data_balls[num_question]["Answers"] if data_balls is not None else answers
    balls = [ball["ball"] for ball in balls]
    return {
        "text_question_answers": question + "\n\n" + answers_str,
        "num_answers": [{"text": f"{num}: {ball} ", "id": f"{num}"} for num, ball in zip(range(1, len(answers) + 1), balls)]
            }


async def conclusion_getter(**kwargs):
    roles = roles_name
    roles_ball = {
        0: 0,
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
        6: 0,
        7: 0
    }

    dialog_manager: DialogManager = kwargs.get("dialog_manager")
    data_balls: dict = dialog_manager.dialog_data.get("data_balls")
    amount_question = len(data_balls)
    for question_index in range(amount_question):
        question: dict = data[question_index]
        for answer_index in range(len(question["Answers"])):
            ball = int(question["Answers"][answer_index]["ball"])
            roles_indexes:[int] = question["Answers"][answer_index]["RoleTeam"]
            for role in roles_indexes:
                roles_ball[role] += ball / len(roles)

    Suit_role = -1
    max_ball = -1
    for role in range(len(roles_ball)):
        if roles_ball[role] > max_ball:
            Suit_role = role
            max_ball = roles_ball[role]

    dialog_manager.dialog_data.clear()
    some_text = "По итогам пройденного теста ваша роль:\n\n"
    some_text2 =  "Хотите пройти тест заново?"
    return {
        "text": some_text + roles_name[Suit_role] + "\n\n" + some_text2
    }

start_window = Window(
    Const(text="Привет, готов пройти тест Белбина?"),
    Row(
        Button(id="1", text=Const("Да!"), on_click=some_handler),
    ),
    state=StartSG.start
)

window_question = Window(
    Format("{text_question_answers}"),
    Select(
        Format('{item[text]}'),
        id="Select",
        item_id_getter = lambda id: id["id"],
        items = "num_answers",
        on_click=answer_handler

    ),
    Button(Const("Далее"), id = "1", on_click=chapter_handler),
    getter=question_getter,
    state=StartSG.window_chapter
)

window_answer = Window(
    Format("{text_question_answers}"),
    Select(
        Format('{item}'),
        id="Select",
        item_id_getter = lambda id: id,
        items = "balls_row1",
        on_click = write_ball_handler
    ),
    Select(
        Format('{item}'),
        id="Select",
        item_id_getter = lambda id: id,
        items = "balls_row2",
        on_click = write_ball_handler
    ),
    getter=answer_getter,
    state=StartSG.window_answer_ball
)

window_conclusion = Window(
    Format("{text}"),
    Button(Const("Пройти тест заново"), id="1", on_click=reset_hndler),
    getter=conclusion_getter,
    state=StartSG.window_conclusion

)

start_dialog = Dialog(
    start_window,
    window_question,
    window_answer,
    window_conclusion
)


# Этот классический хэндлер будет срабатывать на команду /start
@dp.message(CommandStart())
async def command_start_process(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=StartSG.start, mode=StartMode.RESET_STACK)
