
def get_available_models_openai(
        api_key: str, base_url: str = None
) -> dict:
    """Get available models

    Args:
        api_key (str): _description_
        base_url (str, optional): _description_. Defaults to None.

    Returns:
        dict: {'model_id': 'model_provider'}
    """
    from openai import OpenAI

    client = OpenAI(api_key=api_key, base_url=base_url)
    model_list = client.models.list().to_dict()['data']
    result_dict = {model['id']: model['owned_by'] for model in model_list}
    return result_dict


def basic_conversation_openai(
        api_key: str, prompts: list,
        model: str = 'gpt-3.5-turbo', base_url: str = None
) -> str:
    """openai最基本的对话，如果需要使用别的服务提供商，注意修改base_url

    Args:
        api_key (str): _description_
        prompts (list): e.g [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "Hello!"}]
        model (str, optional): _description_. Defaults to 'gpt-3.5-turbo'.
        base_url (str, optional): _description_. Defaults to None.

    Returns:
        str: _description_
    """

    from openai import OpenAI

    client = OpenAI(api_key=api_key, base_url=base_url)
    completion = client.chat.completions.create(model=model, messages=prompts)
    return completion.choices[0].message.content


def text_2_audio_openai(
        api_key: str, text: str, audio_file_path: str = 'speech.mp3',
        voice: str = 'echo', model: str = 'tts-1', base_url: str = None
) -> None:
    """使用openai api从文字生成语音，如果需要使用别的服务提供商，注意修改base_url

    Args:
        api_key (str): _description_
        text (str): _description_
        audio_file_path (str, optional): _description_. Defaults to 'speech.mp3'.
        voice (str, optional): [alloy, echo, fable, onyx, nova, shimmer]. Defaults to 'echo'.
        model (str, optional): _description_. Defaults to 'tts-1'.
        base_url (str, optional): _description_. Defaults to None.
    """
    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.audio.speech.create(
        model=model,
        voice=voice,
        input=text
    )

    # response.stream_to_file(speech_file_path)
    response.write_to_file(audio_file_path)


def audio_2_text_openai(
        api_key: str, audio_file_path: str,
        model: str = 'whisper-1', base_url: str = None
) -> str:
    """使用openai api从语音生成文字，如果需要使用别的服务提供商，注意修改base_url

    Args:
        api_key (str): _description_
        audio_file_path (str): _description_
        model (str, optional): _description_. Defaults to 'whisper-1'.
        base_url (str, optional): _description_. Defaults to None.

    Returns:
        str: _description_
    """
    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url=base_url)

    audio_file = open(audio_file_path, "rb")
    transcription = client.audio.transcriptions.create(
        model=model,
        file=audio_file
    )
    return transcription.text


def get_pandasai_agent(data, openapi_key: str = None, config: dict = None):
    """获得pandas-ai库中的Agent对象: https://docs.pandas-ai.com/en/latest/
        Agent.chat("XXX") or 
        Agent.clarification_question("XXX") or 
        Agent.explain() or 
        Agent.rephrase_query("XXX")


    Args:
        openapi_key (str): 如果不传，使用pandasbi的免费key
        data (_type_): Dataframe or [Dataframe1, Dataframe2, ...]
        config (dict, optional): https://docs.pandas-ai.com/en/latest/getting-started/#config. Defaults to None.

    Returns:
        _type_: pandasai.Agent
    """
    import os

    from pandasai import Agent
    from pandasai.llm import OpenAI

    if not openapi_key:
        os.environ["PANDASAI_API_KEY"] = "$2a$10$AjBzJYa7M.AV8wRfcUisme4ARgSUVF.ooDDIn4MS4S52Umd7N6O12"
        if not config:
            config = {
                "save_logs": False,
                "save_charts": False,
                "verbose": False,
                "enable_cache": False,
                "open_charts": True
            }
    else:
        llm = OpenAI(api_token=openapi_key)
        if not config:
            config = {
                "llm": llm,
                "save_logs": False,
                "save_charts": False,
                "verbose": False,
                "enable_cache": False,
                "open_charts": True
            }
    agent = Agent(data, config)
    return agent


def generate_lobechat_agents(
        agent_csv_path: str, version: int, default_model: str = 'gemini-1.5-pro-latest', model_provider: str = 'google') -> None:
    """生成lobechat的agent导入文件

    Args:
        agent_csv_path (str): _description_
        default_model (str, optional): _description_. Defaults to 'gemini-1.5-pro-latest'.
        model_provider (str, optional): 如果修改了默认model，需要相应提供provider. Defaults to 'google'.
    """
    import json

    import pandas as pd

    df = pd.read_csv(agent_csv_path)
    df.set_index('item', drop=True, inplace=True)

    group_dict = {
        prompts_group.split('.')[0]: prompts_group.split('.')[1]
        for _, prompts_group in df.loc['group'].items()
    }
    session_groups = [
        {
            "name": group_name,
            "id": group_id
        } for group_id, group_name in group_dict.items()
    ]

    whole_dict = {
        "exportType": "agents",
        "version": version,
        "state": {
            "sessionGroups": session_groups,
            "sessions": []
        }
    }

    for prompts_name, prompts_data in df.items():
        prompts_dict = prompts_data.to_dict()
        single_dict = {
            "group": prompts_dict['group'].split('.')[0],
            "pinned": bool(int(prompts_dict['pinned'])),
            "type": "agent",
            "model": default_model,
            "meta": {
                "avatar": prompts_dict['avatar'],
                "title": prompts_name,
                "description": prompts_dict['description'],
            },

            "config": {
                "chatConfig": {
                    "displayMode": "chat",

                    "enableAutoCreateTopic": True,
                    "autoCreateTopicThreshold": 2,

                    "enableCompressThreshold": bool(int(prompts_dict['enableCompressThreshold'])),
                    "compressThreshold": int(prompts_dict['compressThreshold']),

                    "enableHistoryCount": bool(int(prompts_dict['enableHistoryCount'])),
                    "historyCount": int(prompts_dict['historyCount']),

                    "inputTemplate": "" if pd.isna(prompts_dict['inputTemplate']) else prompts_dict['inputTemplate'],
                },

                "model": default_model,

                "params": {
                    "frequency_penalty": 0,
                    "presence_penalty": 0,
                    "temperature": float(prompts_dict['temperature']),
                    "top_p": 1
                },
                "plugins": [],
                "provider": model_provider,
                "systemRole": "" if pd.isna(prompts_dict['prompt']) else prompts_dict['prompt'],
                "tts": {
                    "showAllLocaleVoice": False,
                    "sttLocale": "auto",
                    "ttsService": "openai",
                    "voice": {
                        "openai": "echo"
                    }
                }
            }
        }
        whole_dict["state"]["sessions"].append(single_dict)

    with open(f"lobechat_agents_{default_model}.json", "w", encoding="utf8") as f:
        json.dump(whole_dict, f, ensure_ascii=False)


def clear_lobechat_messages(json_path: str, json_result: str = 'result.json', keep_favorites: bool = True) -> None:
    """clear all messages and topics in lobechat json file, except for the favorites.

    Args:
        json_path (str): _description_
        json_result (str, optional): _description_. Defaults to 'result.json'.
        keep_favorites (bool, optional): _description_. Defaults to True.
    """
    import json
    record = None
    with open(json_path, 'r') as f:
        record = json.load(f)
    record['data']['messagePlugins'] = []
    record['data']['messageTranslates'] = []

    if keep_favorites:
        topics = []
        favorite_topic_id = []
        for topic in record['data']['topics']:
            if topic['favorite'] == True:
                topics.append(topic)
                favorite_topic_id.append(topic['id'])
        record['data']['topics'] = topics

        new_messages = []
        for message in record['data']['messages']:
            if message['topicId'] in favorite_topic_id:
                new_messages.append(message)
        record['data']['messages'] = new_messages
    else:
        record['data']['topics'] = []
        record['data']['messages'] = []
    with open(json_result, 'w') as f:
        json.dump(record, f, indent=4)
