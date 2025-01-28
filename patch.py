import gptme.llm.models
import gptme.llm.llm_openai
import gptme.util.reduce
import gptme.prompts
import gptme
import openai
import types

def reset_var(var, new_value, _dict=gptme.__dict__, ignore=set(), last_val=None, upd_globals={}):
    if _dict["__name__"] in ignore:
        return
    ignore.append(_dict["__name__"])
    updated = []
    for key, value in _dict.items():
        if key == var or key.endswith(f".{var}"):
            if not last_val:
                _dict[key] = new_value
        if last_val and type(last_val) is type(value) and last_val == value:
            #_dict[key] = new_value
            value.__code__ = new_value.__code__
            updated.append((value.__globals__, upd_globals))
        if type(value) == types.ModuleType:
            reset_var(var, new_value, value.__dict__, ignore, last_val, upd_globals)
    for k, v in updated:
        k.update(v)

    
gptme.llm.models.PROVIDERS = gptme.llm.models.PROVIDERS + ("qwen", )
gptme.llm.models.PROVIDERS_OPENAI.append("qwen")
gptme.llm.models.MODELS["qwen"] = {
    "qwen2.5-coder-32b-instruct": {
        "context": 131_072,
        "max_output": 8192,
        "price_input": 0,
        "price_output": 0
    },
    "qvq-72b-preview": {
        "context": 32_768,
        "max_output": 8192,
        "price_input": 0,
        "price_output": 0,
        "supports_vision": True
    },
    "qwen-plus-latest": {
        "context": 131_072,
        "max_output": 8192,
        "price_input": 0,
        "price_output": 0,
        "supports_vision": True
    },
    "qwq-32b-preview": {
        "context": 131072,
        "max_output": 8192,
        "price_input": 0,
        "price_output": 0
    },
    "qwen-vl-max-latest": {
        "context": 32_768,
        "max_output": 2048,
        "price_input": 0,
        "price_output": 0,
        "supports_vision": True
    },
    "qwen-turbo-latest": {
        "context": 1000_000,
        "max_output": 8192,
        "price_input": 0,
        "price_output": 0
    },
    "qwen2.5-72b-instruct": {
        "context": 131_072,
        "max_output": 8192,
        "price_input": 0,
        "price_output": 0
    },
    "qwen2.5-32b-instruct": {
        "context": 131072,
        "max_output": 8192,
        "price_input": 0,
        "price_output": 0
    }
}



def new_reduce_log(log, limit, prev_len):
    model = get_default_model() or get_model("gpt-4")
    if "qwen" in model.model:
        for i, message in enumerate(log):
            if i > 0 and message.role == "system":
                log[i] = Message("user", f"System: {message.content}", pinned=message.pinned,
                                 hide=message.hide, quiet=message.quiet, timestamp=message.timestamp,
                                 files=message.files, call_id=message.call_id)
    return original_reduce_log(log, limit, prev_len)
original_reduce_log = gptme.util.reduce.reduce_log.__new__(type(gptme.util.reduce.reduce_log),
                                                           gptme.util.reduce.reduce_log.__code__,
                                                           gptme.util.reduce.reduce_log.__globals__) 


last_content_length = 0
original_process_response_data = openai._base_client.BaseClient._process_response_data
def new_process_response_data(self, *, data, cast_to, response):
    global last_content_length
    if "chat.qwenlm.ai" in str(response.url):
        content = data["choices"][0]["delta"]["content"]
        if len(content) < last_content_length:
            last_content_length = 0
        new_content = content[last_content_length:]
        data["choices"][0]["delta"]["content"] = new_content
        last_content_length = len(content)
    return original_process_response_data(self, data=data, cast_to=cast_to, response=response)
openai._base_client.BaseClient._process_response_data = new_process_response_data


original_prompt_gptme = gptme.prompts.prompt_gptme
def new_prompt_gptme(interactive):
    base_prompt = f"""
You are AIWE, a universal AI web site editor powered by LLMs.
You are designed for creating, editing, and debugging websites.
You will create fully functional websites based on the following stack:
- Python
- FastAPI
- SQLAlchemy(Postgresql)
- Jinja2
- HTML
- CSS
- JavaScript
- Tailwind(CDN)

Use this knowledge when solving user tasks:
- Recommendations from the book Chris Coyier “CSS Grid Layout: Complete Guide” 2022
- Recommendations from the book Aarron Walter "Designing for Emotion: What Neuroscience Can Teach Us About Web Usability" 2013
- Recommendations from the book Lea Verou “CSS Secrets” 2017
- Recommendations from the book Chris Box “Selling on Behavior” 2013
- Recommendations from the book Bryan H. Smith “Never Split the Difference: Negotiating As If Your Life Depended On It” 2016
- Recommendations from the book Mariano Anaya "Clean Code in Python: Refactor your legacy code base" 2018
- ThemeForest template library

When designing pages:
1. Use a component-based approach:
- Break pages into reusable components
- Use Tailwind and Font Awesome Free
- Create separate files for each component
- Always create responsive layouts
2. Always use responsive design:
- Start with the mobile version (mobile-first)
- Use Tailwind breakpoints (sm, md, lg, xl, 2xl)
3. Structure and semantics:
- Use semantic HTML tags
- Follow the correct hierarchy of headings
- Ensure accessibility (aria-attributes)
4. Optimization:
- Optimize images
- Use lazy loading where necessary
- Follow performance principles
5. Styling:
- Use Tailwind utilities for:
-- Flexbox and Grid layouts
-- Margins and positioning
-- Colors and typography
-- Animations and transitions
- Use Font Awesome Free
6. Monitor backend and frontend compatibility


When writing the Backend:
1. Pay attention to architecture:
- Split code into modules
- Split modules into separate files
- Ensure that each module file has no more than 80-100 lines
2. Add necessary dependencies to requirements.txt
3. Document the project structure in README.md

When encountering issues:
1. Read the file using the appropriate command
2. If you cannot resolve the issue on the first try - use save instead of patch

Possible issues:
1. Errors in Python code execution
2. Identical requests from the user

You can run code, execute terminal commands, and access the filesystem on the local machine.
You will help the user with writing code, either from scratch or in existing projects.
You will think step by step when solving a problem, in `<thinking>` tags.
Break down complex tasks into smaller, manageable steps.

You have the ability to self-correct.
If you receive feedback that your output or actions were incorrect, you should:
- acknowledge the mistake
- analyze what went wrong in `<thinking>` tags
- provide a corrected response

You should learn about the context needed to provide the best help,
such as exploring the current working directory and reading the code using terminal tools.

When suggesting code changes, prefer applying patches over examples. Preserve comments, unless they are no longer relevant.
Use the patch tool to edit existing files, or the save tool to overwrite.
When the output of a command is of interest, end the code block and message, so that it can be executed before continuing.

Do not use placeholders like `$REPO` unless they have been set.
Do not suggest opening a browser or editor, instead do it using available tools.

Always prioritize using the provided tools over suggesting manual actions.
Be proactive in using tools to gather information or perform tasks.
When faced with a task, consider which tools might be helpful and use them.
Always consider the full range of your available tools and abilities when approaching a problem.

Maintain a professional and efficient communication style. Be concise but thorough in your explanations.

Use `<thinking>` tags to think before you answer.""".strip()

    interactive_prompt = """
You are in interactive mode. The user is available to provide feedback.
You should show the user how you can use your tools to write code, interact with the terminal, and access the internet.
The user can execute the suggested commands so that you see their output.
If the user aborted or interrupted an operation don't try it again, ask for clarification instead.
If clarification is needed, ask the user.
""".strip()

    non_interactive_prompt = """
You are in non-interactive mode. The user is not available to provide feedback.
All code blocks you suggest will be automatically executed.
Do not provide examples or ask for permission before running commands.
Proceed directly with the most appropriate actions to complete the task.
""".strip()

    full_prompt = (
        base_prompt
        + "\n\n"
        + (interactive_prompt if interactive else non_interactive_prompt)
    )
    yield gptme.Message("system", full_prompt)
gptme.prompts.prompt_gptme = new_prompt_gptme


def init(provider, config):
    global openai
    from openai import AzureOpenAI, OpenAI  # fmt: skip

    if provider == "openai":
        api_key = config.get_env_required("OPENAI_API_KEY")
        openai = OpenAI(api_key=api_key)
    elif provider == "azure":
        api_key = config.get_env_required("AZURE_OPENAI_API_KEY")
        azure_endpoint = config.get_env_required("AZURE_OPENAI_ENDPOINT")
        openai = AzureOpenAI(
            api_key=api_key,
            api_version="2023-07-01-preview",
            azure_endpoint=azure_endpoint,
        )
    elif provider == "openrouter":
        api_key = config.get_env_required("OPENROUTER_API_KEY")
        openai = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
    elif provider == "gemini":
        api_key = config.get_env_required("GEMINI_API_KEY")
        openai = OpenAI(
            api_key=api_key, base_url="https://generativelanguage.googleapis.com/v1beta"
        )
    elif provider == "xai":
        api_key = config.get_env_required("XAI_API_KEY")
        openai = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
    elif provider == "qwen":
        api_key = config.get_env_required("QWEN_API_KEY")
        openai = OpenAI(api_key=api_key, base_url="https://chat.qwenlm.ai/api")
    elif provider == "groq":
        api_key = config.get_env_required("GROQ_API_KEY")
        openai = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
    elif provider == "deepseek":
        api_key = config.get_env_required("DEEPSEEK_API_KEY")
        openai = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
    elif provider == "local":
        # OPENAI_API_BASE renamed to OPENAI_BASE_URL: https://github.com/openai/openai-python/issues/745
        api_base = config.get_env("OPENAI_API_BASE")
        api_base = api_base or config.get_env("OPENAI_BASE_URL")
        if not api_base:
            raise KeyError("Missing environment variable OPENAI_BASE_URL")
        api_key = config.get_env("OPENAI_API_KEY") or "ollama"
        openai = OpenAI(api_key=api_key, base_url=api_base)
    else:
        raise ValueError(f"Unknown provider: {provider}")

    assert openai, "Provider not initialized"
    

reset_var("PROVIDERS", gptme.llm.models.PROVIDERS, ignore=list())
reset_var("PROVIDERS_OPENAI", gptme.llm.models.PROVIDERS_OPENAI, ignore=list())
reset_var("MODELS", gptme.llm.models.MODELS, ignore=list())
reset_var("reduce_log", new_reduce_log, ignore=list(), last_val=gptme.util.reduce.reduce_log, upd_globals={"original_reduce_log": original_reduce_log})
#reset_var("prompt_gptme", gptme.prompts.prompt_gptme, ignore=list())
reset_var("_process_response_data", openai, ignore=list())
reset_var("init", init, ignore=list(), last_val=gptme.llm.llm_openai.init)
