"""
AI providers for Commit-Gen.
"""

import re
import sys
from typing import Optional

import requests

from .config import (
    get_provider_info,
    get_base_url,
    DEFAULT_PROMPT,
    SIMPLE_OLLAMA_PROMPT,
)


def clean_commit_message(message: str) -> str:
    """Clean the commit message by removing escape sequences and extra whitespace."""
    # Replace escaped newlines with actual newlines
    message = message.replace("\\n", "\n")
    # Remove escaped carriage returns
    message = message.replace("\\r", "")
    # Remove leading and trailing whitespace from each line
    message = "\n".join(line.strip() for line in message.split("\n"))
    # Remove other escaped characters like \t, \b, etc.
    message = re.sub(r"\\[a-zA-Z]", "", message)
    return message


def generate_commit_message_ollama(
        model: str, changes: str, custom_prompt: Optional[str] = None
) -> str:
    """Generate commit message using Ollama."""
    provider_info = get_provider_info("ollama")
    base_url = provider_info["base_url"]
    endpoint = provider_info["endpoint"]

    # Handle the custom prompt differently if it's a changelog prompt
    if custom_prompt and "commit_list is a JSON object" in custom_prompt:
        # For changelog, the custom_prompt is already fully formatted
        prompt = custom_prompt
    elif custom_prompt:
        prompt = custom_prompt.format(changes=changes)
    else:
        prompt = SIMPLE_OLLAMA_PROMPT.format(changes=changes)

    request_body = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(f"{base_url}/{endpoint}", headers=headers, json=request_body)
        response.raise_for_status()
        response_data = response.json()

        commit_message = response_data.get("response", "")
        if not commit_message:
            print(f"Error: Failed to get response from Ollama. Response: {response.text}")
            sys.exit(1)

        return clean_commit_message(commit_message)
    except requests.exceptions.RequestException as e:
        print(f"Error making request to Ollama: {str(e)}")
        sys.exit(1)


def generate_commit_message_openrouter(
        api_key: str, model: str, changes: str, diff_content: str, custom_prompt: Optional[str] = None
) -> str:
    """Generate commit message using OpenRouter."""
    provider_info = get_provider_info("openrouter")
    base_url = get_base_url() or provider_info["base_url"]
    endpoint = provider_info["endpoint"]

    headers = {
        "HTTP-Referer": "*",
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Title": "cmai - AI Commit Message Generator",
    }

    # Handle the custom prompt differently if it's a changelog prompt
    if custom_prompt and "commit_list is a JSON object" in custom_prompt:
        # For changelog, the custom_prompt is already fully formatted
        user_content = custom_prompt
    elif custom_prompt:
        user_content = custom_prompt.format(changes=changes, diff_content=diff_content)
    else:
        user_content = DEFAULT_PROMPT.format(changes=changes, diff_content=diff_content)

    request_body = {
        "model": model,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": "You are a git commit message generator. Create conventional commit messages.",
            },
            {
                "role": "user",
                "content": user_content,
            },
        ],
    }

    try:
        response = requests.post(f"{base_url}/{endpoint}", headers=headers, json=request_body)
        response.raise_for_status()
        response_data = response.json()

        commit_message = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not commit_message:
            print(f"Error: Failed to get response from OpenRouter. Response: {response.text}")
            sys.exit(1)

        return clean_commit_message(commit_message)
    except requests.exceptions.RequestException as e:
        print(f"Error making request to OpenRouter: {str(e)}")
        sys.exit(1)


def generate_commit_message_gemini(
        api_key: str, model: str, changes: str, diff_content: str, custom_prompt: Optional[str] = None
) -> str:
    """Generate commit message using Google Gemini."""
    provider_info = get_provider_info("gemini")
    base_url = get_base_url() or provider_info["base_url"]
    endpoint = provider_info["endpoint"].format(model=model)

    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json",
    }

    # Handle the custom prompt differently if it's a changelog prompt
    if custom_prompt and "commit_list is a JSON object" in custom_prompt:
        # For changelog, the custom_prompt is already fully formatted
        user_content = custom_prompt
    elif custom_prompt:
        user_content = custom_prompt.format(changes=changes, diff_content=diff_content)
    else:
        user_content = DEFAULT_PROMPT.format(changes=changes, diff_content=diff_content)

    request_body = {
        "contents": [
            {
                "parts": [
                    {
                        "text": user_content
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(f"{base_url}/{endpoint}", headers=headers, json=request_body)
        response.raise_for_status()
        response_data = response.json()

        commit_message = response_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text",
                                                                                                               "")
        if not commit_message:
            print(f"Error: Failed to get response from Gemini. Response: {response.text}")
            sys.exit(1)

        return clean_commit_message(commit_message)
    except requests.exceptions.RequestException as e:
        print(f"Error making request to Gemini: {str(e)}")
        sys.exit(1)


def generate_commit_message_mistral(
        api_key: str, model: str, changes: str, diff_content: str, custom_prompt: Optional[str] = None
) -> str:
    """Generate commit message using Mistral AI."""
    provider_info = get_provider_info("mistral")
    base_url = get_base_url() or provider_info["base_url"]
    endpoint = provider_info["endpoint"]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Handle the custom prompt differently if it's a changelog prompt
    if custom_prompt and "commit_list is a JSON object" in custom_prompt:
        # For changelog, the custom_prompt is already fully formatted
        user_content = custom_prompt
    elif custom_prompt:
        user_content = custom_prompt.format(changes=changes, diff_content=diff_content)
    else:
        user_content = DEFAULT_PROMPT.format(changes=changes, diff_content=diff_content)

    request_body = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a git commit message generator. Follow Conventional Commits. Return ONLY the commit message, no explanations, no code blocks, no extra characters.",
            },
            {
                "role": "user",
                "content": user_content,
            },
        ],
        "max_tokens": 1000,
        "temperature": 0.1,
    }

    try:
        response = requests.post(f"{base_url}/{endpoint}", headers=headers, json=request_body)
        response.raise_for_status()
        response_data = response.json()

        commit_message = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not commit_message:
            print(f"Error: Failed to get response from Mistral AI. Response: {response.text}")
            sys.exit(1)

        return clean_commit_message(commit_message)
    except requests.exceptions.RequestException as e:
        print(f"Error making request to Mistral AI: {str(e)}")
        sys.exit(1)


def generate_commit_message_custom(
        api_key: str, model: str, changes: str, diff_content: str, custom_prompt: Optional[str] = None
) -> str:
    """Generate commit message using a custom provider."""
    base_url = get_base_url()
    if not base_url:
        print("Error: Custom provider requires base URL to be set")
        sys.exit(1)

    endpoint = "chat/completions"

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    # Handle the custom prompt differently if it's a changelog prompt
    if custom_prompt and "commit_list is a JSON object" in custom_prompt:
        # For changelog, the custom_prompt is already fully formatted
        user_content = custom_prompt
    elif custom_prompt:
        user_content = custom_prompt.format(changes=changes, diff_content=diff_content)
    else:
        user_content = DEFAULT_PROMPT.format(changes=changes, diff_content=diff_content)

    request_body = {
        "model": model,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": "You are a git commit message generator. Create conventional commit messages.",
            },
            {
                "role": "user",
                "content": user_content,
            },
        ],
    }

    try:
        response = requests.post(f"{base_url}/{endpoint}", headers=headers, json=request_body)
        response.raise_for_status()
        response_data = response.json()

        commit_message = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not commit_message:
            print(f"Error: Failed to get response from custom provider. Response: {response.text}")
            sys.exit(1)

        return clean_commit_message(commit_message)
    except requests.exceptions.RequestException as e:
        print(f"Error making request to custom provider: {str(e)}")
        sys.exit(1)


def generate_commit_message(
        provider: str,
        api_key: str,
        model: str,
        changes: str,
        diff_content: str,
        custom_prompt: Optional[str] = None,
) -> str:
    """Generate commit message using the specified provider."""
    if provider == "ollama":
        return generate_commit_message_ollama(model, changes, custom_prompt)
    elif provider == "openrouter":
        return generate_commit_message_openrouter(api_key, model, changes, diff_content, custom_prompt)
    elif provider == "gemini":
        return generate_commit_message_gemini(api_key, model, changes, diff_content, custom_prompt)
    elif provider == "mistral":
        return generate_commit_message_mistral(api_key, model, changes, diff_content, custom_prompt)
    elif provider == "custom":
        return generate_commit_message_custom(api_key, model, changes, diff_content, custom_prompt)
    else:
        print(f"Error: Unknown provider '{provider}'")
        sys.exit(1)
