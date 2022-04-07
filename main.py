import redis
from environs import Env


def open_file(file_path, encoding='UTF-8'):
    with open(file_path, 'r', encoding=encoding) as file:
        text = file.read()
    return text


def split_note(note):
    separated_note = note.split('\n\n')
    for note_part in separated_note:
        if note_part.startswith('Вопрос'):
            _, question_text = note_part.split('\n', maxsplit=1)
        elif note_part.startswith('Ответ'):
            _, answer_text = note_part.split('\n', maxsplit=1)
            return question_text, answer_text


def main():
    env = Env()
    env.read_env()

    redis_host = env.str('REDIS_DB_NAME')
    redis_port = env.int('REDIS_PORT')
    redis_pass = env.str('REDIS_PASSWORD')

    r = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_pass,
        db=0
    )

    file_path = 'questions/1vs1201.txt'
    new_questions = open_file(file_path, encoding='KOI8-R').split("\n\n\n")
    for note in new_questions:
        question_text, answer_text = split_note(note)
        r.set(question_text, answer_text)


if __name__ == "__main__":
    main()
