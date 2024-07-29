from utils.preprocessing import read_pdf
import transformers
import torch

MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"

def format_analyses(user_input: str) -> str:
    pipeline = transformers.pipeline(
        "text-generation",
        model=MODEL_ID,
        model_kwargs={"torch_dtype": torch.bfloat16},
        device_map="auto",
    )
    messages = [
    {"role": "system", "content": """You are a text formatter, you get a text in a free form with laboratory analyses of patients, you must transform it into strings like 'ANALYSIS_NAME has a value of ANALYSIS_VALUE, it measured in UNIT_OF_MEASURE and has a reference range of normal values between MINIMUM VALUE (if missing = 0) and MAXIMUM VALUE (if missing = Infinity).' Dont provide any additional text beside strings with analyses information, it's important!
    """},
    {"role": "user", "content": user_input}
    ]

    terminators = [
    pipeline.tokenizer.eos_token_id,
    pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]
    outputs = pipeline(
        messages,
        max_new_tokens=3000,
        eos_token_id=terminators,
        do_sample=True,
        temperature=0.6,
        top_p=0.9,
    )
    with open('log_analyses.txt', 'w') as f:
        f.write(user_input)
        f.write('\n')
        f.write(str(outputs[0]["generated_text"]))
    return (outputs[0]["generated_text"][-1]['content']).replace('<', ' less than ').replace('>', ' greater than ')


def add_state(analyses: str) -> str:
    print(MODEL_ID)
    pipeline = transformers.pipeline(
        "text-generation",
        model=MODEL_ID,
        model_kwargs={"torch_dtype": torch.bfloat16},
        device_map="auto",
    )
    messages = [
    {"role": "system", "content": """You are a text analyser, you will get a bunch os sentances about results of lab analyses. Please return a short summary in this format: 'Analysis name - State'. 'State' is categorical and can have only 3 values: 'Low', 'High', 'Normal'. Decimal separator in text is a point. If you dont see reference range in recieved text, please, try to evaluate state on your own. Dont provide any additional text besides summary, it's important!
    Examples: 
    Input:
    Kek has a value of 40.7, it measured in мкмоль/л and has a reference range of normal values 5.8 - 50.5.
    // Kek value is greater than minimum normal reference (5.8) and less than maximum normal reference (50.5) so the state should be Normal
    Output:
    Kek - Normal

    Input:
    Lol has a value of 4.660, it measured in μIU/ml and has a reference range of normal values 0.27-4.2.
    // Lol of 4.66 is bigger than the maximum normal reference (4.2) and bigger than the minimum normal reference (0.27) so the state should be 'High'
    Output:
    Lol - High

    Input:
    Krek has a value of 45.9, it measured in IU/l and has a reference range of normal values < 41.
    // All Krek value less than 41 is normal, but we have a greater value of 45.9 so state should be 'High'
    Output:
    Krek - High

    Input:
    Experimental test has a value of 33.9, it measured in IU/l and has a reference range of normal values > 41.
    // All experimental test value greater than 41 is normal, but we have a less value of 33.9 so state should be 'Low'
    Output:
    Experimental test - Low

    Input:
    Owo has a value of 31.6, it measured in IU/l and has a reference range of normal values < 40.
    Uwu has a value of 0.89, it measured in % and has a reference range of normal values 0.8-1.14.
    // Owo value less than 40 is normal and we have a value of 31.6 so state should be 'Normal'
    // Uwu value must be greater than 0.8 and less than 1.14 so for 0.89 value State should be 'Normal'
    Output:
    Owo - Normal
    Uwu - Normal
    """},
    {"role": "user", "content": analyses}
    ]
    terminators = [
    pipeline.tokenizer.eos_token_id,
    pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]
    outputs = pipeline(
        messages,
        max_new_tokens=3000,
        eos_token_id=terminators,
        do_sample=True,
        temperature=0.6,
        top_p=0.9,
    )
    with open('log_analyses.txt', 'w') as f:
        f.write(analyses)
        f.write('\n')
        f.write(str(outputs[0]["generated_text"]))

    return (outputs[0]["generated_text"][-1]['content'])


def predict_diagnoses(analyses: str) -> str:
    pipeline = transformers.pipeline(
        "text-generation",
        model=MODEL_ID,
        model_kwargs={"torch_dtype": torch.bfloat16},
        device_map="auto",
    )
    messages = [
    {"role": "system", "content": f"Please analyze the user-provided CSV table containing laboratory test results. Columns of the data are the following: Analysis, Value, Reference minimum value, Reference maximum value, Unit of Measure. If the analysis values more than minimum reference value and less than reference maximum value, they are considered normal, in any other case it is abnormal! If You may provide a diagnosis if confident, suggest further tests if more information is needed, and recommend a specialist to consult if there are suspicions of any conditions beyond the current analysis. Please format this text to support sending by telegram bot with HTML Parser."},
    {"role": "user", "content": analyses}
    ]   
    terminators = [
    pipeline.tokenizer.eos_token_id,
    pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]
    outputs = pipeline(
        messages,
        max_new_tokens=3000,
        eos_token_id=terminators,
        do_sample=True,
        temperature=0.6,
        top_p=0.9,
    )
    with open('log_diagnoses.txt', 'w') as f:
        f.write(analyses)
        f.write('\n')
        f.write(str(outputs[0]["generated_text"][-1]['content']))

    return (outputs[0]["generated_text"][-1]['content'])
