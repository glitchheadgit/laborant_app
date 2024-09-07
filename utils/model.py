import openai
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
    table = response.choices[0].message['content'].strip().replace("'", "")
    print(table)
    df = pd.read_csv(StringIO(table))	
    print(df)    
    df["Value"] = df['Value'].astype(float)
    df['Deviation'] = df.apply(check_deviation, axis=1)
    print(df)
    table_text_deviations = filter_deviations(df)
    return df.to_csv(index=False), table_text_deviations


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


def analyze_table_with_gpt(prompt, temperature=0.15, max_tokens=3000):
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