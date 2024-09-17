import openai
import tiktoken
import pandas as pd

from io import StringIO
from utils.preprocessing import read_pdf
from config_reader import config

openai.api_key = config.gpt_token.get_secret_value()

def retrieve_table_from_text(user_input: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": config.system_content_table.get_secret_value()},
            {"role": "user", "content": user_input},
        ],
        temperature=0.1,
        max_tokens=3000
    )
    table = response.choices[0].message['content'].strip()
    
    table_lines = table.strip().split("\n")
    cleaned_lines = []

    # Обрабатываем каждую строку
    for line in table_lines:
        parts = line.split("','")
        
        # Если это не заголовок, обрабатываем столбец Analysis
        if parts[0].startswith("'") and parts[0].endswith("'"):
            analysis_value = parts[0].strip("'")
            analysis_value = analysis_value.replace(",", " ")
            parts[0] = f"'{analysis_value}'"
        
        # Собираем строку обратно
        cleaned_line = "','".join(parts)
        cleaned_lines.append(cleaned_line)

    # Собираем очищенную таблицу обратно в текст
    cleaned_table = "\n".join(cleaned_lines)

    print("Очищенная таблица (после удаления запятых в Analysis):")
    print(cleaned_table)
    
    table_text_deviation = "Не получилось обработать таблицу из-за наличия букв/слов в значениях стобцов 'Value' и 'Reference Value'. Поэтому сам из таблицы указанной в input data составь таблицу Blood values that are abnormal, оставив строки только с теми показателями крови, значения которых отличаются от референсных."

    try:
        # Преобразуем очищенный текст в DataFrame
        df = pd.read_csv(StringIO(cleaned_table), quotechar="'", sep=',')
        print(df)   
        df["Value"] = df['Value'].astype(float)
        df['Deviation'] = df.apply(check_deviation, axis=1)
        print(df)
        table_text_deviation = filter_deviations(df)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    
    return df.to_csv(index=False), table_text_deviation


def check_deviation(row) -> str:
    reference_value = row['Reference Value'].strip("'")
    value = row['Value']

    if '-' in reference_value:
        lower_bound, upper_bound = map(float, reference_value.split('-'))
        if value < lower_bound:
            return 'Понижен'
        elif value > upper_bound:
            return 'Повышен'
        else:
            return 'В норме'
    elif '<' in reference_value:
        upper_bound = float(reference_value.replace('<', '').replace('=', '').strip())
        if value >= upper_bound:
            return 'Повышен'
        else:
            return 'В норме'
    elif '>' in reference_value:
        lower_bound = float(reference_value.replace('>', '').replace('=', '').strip())
        if value <= lower_bound:
            return 'Понижен'
        else:
            return 'В норме'
    else:
        return 'Неопределено'


def filter_deviations(df) -> str:
    return df[df['Deviation'].isin(['Понижен', 'Повышен'])].to_string(index=False)


def analyze_table_with_gpt(prompt, temperature=0.1, max_tokens=3000):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": config.system_content_analyzer.get_secret_value()},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        n=1,
        stop=None
    )

    return response.choices[0].message['content'].strip()

def count_tokens(text: str) -> int:
    #  Для экономии считаем кол-во токенов в запросе и умножаем на 2 потом.
    encoding = tiktoken.encoding_for_model("gpt-4o-mini")
    tokens = encoding.encode(text)
    return len(tokens)

def getting_bioethic_response(analyses, temperature=0.1):
    # Подсчет количества токенов в prompt
    token_count = count_tokens(analyses)
    
    # Установка значения max_tokens (умножаем на 2)
    max_tokens = token_count * 2

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": config.system_content_bioethic.get_secret_value()},
            {"role": "user", "content": analyses},
        ],
        temperature=temperature,
        max_tokens=max_tokens,  # Используем динамически рассчитанное значение
        n=1,
        stop=None
    )

    return response.choices[0].message['content'].strip()