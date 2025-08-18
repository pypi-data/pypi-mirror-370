"""
Limerick Generator Module

A Python module that connects to OpenAI's ChatGPT API to generate limericks on specified topics.
"""

import os
import json
import yaml
from openai import OpenAI

# Supported OpenAI models for limerick generation
SUPPORTED_MODELS = [
    "gpt-3.5-turbo",
    "gpt-4",
    "gpt-5",
    "gpt-5-mini",
    "gpt-5-nano"
]

# Supported output formats
SUPPORTED_OUTPUT_FORMATS = [
    "text",
    "json",
    "yaml"
]

filth_level_map = [
    ("cheeky and family friendly", "clever and funny."),
    ("risque", "funny and innuendo-filled, without being overly explicit."),
    ("dirty", "sexually charged and innuendo-filled."),
    ("filthy", "offensive, disgusting, full of innuendo and sexual double meanings."),
]
def generate_limerick(topic, api_key = None, model= "gpt-3.5-turbo", filth_level=0, output="text"):
    """
    Generate a limerick about a specified topic using OpenAI's ChatGPT API.
    
    Args:
        topic (str): The topic or theme for the limerick
        api_key (str, optional): OpenAI API key. If not provided, will use OPENAI_API_KEY environment variable
        model (str, optional): OpenAI model to use. Defaults to "gpt-3.5-turbo". 
                              Supported models: gpt-3.5-turbo, gpt-4, gpt-5, gpt-5-mini, gpt-5-nano
        filth_level (int, optional): Content filth level from 0-3. Defaults to 0 (family-friendly).
                                   0: Cheeky and family friendly
                                   1: Risque with innuendo
                                   2: Dirty and sexually charged
                                   3: Filthy and offensive
        output (str, optional): Output format. Defaults to "text".
                               Supported formats: text, json, yaml
    
    Returns:
        str: A generated limerick about the specified topic (text), 
             or the full OpenAI response in JSON/YAML format
    
    Raises:
        ValueError: If no API key is provided, topic is invalid, unsupported model/filth_level/output is specified
        Exception: If there's an error communicating with the OpenAI API
    """
    
    # Validate input
    if not topic or not isinstance(topic, str):
        raise ValueError("Topic must be a non-empty string")
    
    # Validate model
    if model not in SUPPORTED_MODELS:
        raise ValueError(
            f"Unsupported model '{model}'. Supported models are: {', '.join(SUPPORTED_MODELS)}"
        )
    
    # Validate filth
    if type(filth_level) != int or not (0 <= filth_level <= 3):
        raise ValueError(f"Unsupported filth ({filth_level}). Must be an integer in the range 0 - 3 inclusive.")
    
    # Validate output format
    if output not in SUPPORTED_OUTPUT_FORMATS:
        raise ValueError(
            f"Unsupported output format '{output}'. Supported formats are: {', '.join(SUPPORTED_OUTPUT_FORMATS)}"
        )
    
    # Get API key from parameter or environment variable
    if api_key is None:
        api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        raise ValueError(
            "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable "
            "or pass the api_key parameter."
        )
    
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        limerick_type, limerick_description = filth_level_map[filth_level]

        # Instructions for limerick structure
        instructions = f"""
You are a creative poet who specializes in writing {limerick_type} limericks. 
A limerick is a humorous five-line poem with an AABBA rhyme scheme. 
The first, second, and fifth lines should have 7-10 syllables and rhyme with each other.
The last word of the first line should be a place name, but doesn't have to be. It can also be a name or a adjective relating to the main subject.
The third and fourth lines should have 5-7 syllables and rhyme with each other, but should not rhyme with the first two lines.
The last word of each line must be unique (no repeated end-words).
Keep the meter close to anapestic (da-da-DUM) for each line.
Make it {limerick_description}
End with a satisfying punchline or twist.
Please respond with only the limerick, no additional text or explanation."""

        response = client.responses.create(
            model=model,
            instructions=instructions,
            input=f"Please write a {limerick_type} limerick about {topic}",
        )
        
        # Handle different output formats
        if output == "text":
            # Extract just the limerick text (default behavior)
            if response.output_text:
                return response.output_text
            else:
                raise Exception(f"No content returned from {model} model")
        elif output == "json":
            # Return full response as JSON
            response_dict = response.model_dump() if hasattr(response, 'model_dump') else response.__dict__
            return json.dumps(response_dict, indent=2)
        elif output == "yaml":
            # Return full response as YAML
            response_dict = response.model_dump() if hasattr(response, 'model_dump') else response.__dict__
            return yaml.dump(response_dict, default_flow_style=False, indent=2)
        
    except Exception as e:
        raise Exception(f"Error generating limerick: {str(e)}")
