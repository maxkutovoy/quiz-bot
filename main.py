

def main():
    with open('questions/1vs1200.txt', 'r', encoding='KOI8-R') as file:
        text = file.read()
        questions_list = text.split("\n\n\n")
        
    questions = {}
    answers = {}

    for entry in questions_list:
        print(entry)
        entry = entry.split('\n\n')
        for note in entry:

            if note.startswith('Вопрос'):
                question_number, question_text = note.split('\n', maxsplit=1)
            elif note.startswith('Ответ'):
                answer_number, answer_text = note.split('\n', maxsplit=1)
                questions[question_number] = {
                    'question': question_text,
                    'answer': answer_text
                }


if __name__ == "__main__":
    main()
