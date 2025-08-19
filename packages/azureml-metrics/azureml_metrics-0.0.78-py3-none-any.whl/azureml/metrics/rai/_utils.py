# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml.metrics.common.exceptions import MetricsException


def parse_simulator_conversation_history(conversation):
    """
    Parses the conversation history from the simulator.
    :param conversation: The conversation dictionary from the simulator.
    :return: A string of conversation history.
    """
    turns = []
    try:
        for turn in conversation["conversation"]:
            actor = turn["actor"]
            msg = turn["response"].replace("<|im_Start|>", "").replace("<|im_End|>", "")
            if actor == "ChatBot" or actor == "Chatbot":
                actor = "Assistant"
            turns.append(f"({actor}): {msg}")
    except KeyError:
        raise MetricsException("Conversation history ill formatted.")
    return "\n".join(turns)


def parse_simulator_context(conversation):
    """
    Parses the conversation context from the simulator.
    :param conversation: The conversation dictionary from the simulator.
    :return: A string of conversation context.
    """
    context = ""
    try:
        metadata = conversation["meta_data"]["meta_data"]
        context = str(metadata)
    except KeyError:
        raise MetricsException("Conversation context ill formatted.")
    return context


def parse_persona_name(conversation):
    """
    Parses the persona name from the simulator.
    :param conversation: The conversation dictionary from the simulator.
    :return: A string of persona name.
    """
    persona_name = ""
    try:
        persona_name = conversation["meta_data"]["name"]
    except KeyError:
        raise MetricsException("Persona name ill formatted.")
    return persona_name
