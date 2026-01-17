import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    # API Settings (OpenAI Compatible)
    # All sensitive values should be set in .env file
    # See .env.example for template
    
    API_KEY = os.getenv("LLM_API_KEY")
    BASE_URL = os.getenv("LLM_BASE_URL")
    MODEL_NAME = os.getenv("LLM_MODEL")
    
    # Validate required environment variables
    if not API_KEY:
        raise ValueError("LLM_API_KEY not found in environment variables. Please set it in .env file.")
    if not BASE_URL:
        raise ValueError("LLM_BASE_URL not found in environment variables. Please set it in .env file.")
    if not MODEL_NAME:
        raise ValueError("LLM_MODEL not found in environment variables. Please set it in .env file.")

    # Translation Settings
    MAX_CONCURRENCY = int(os.getenv("MAX_CONCURRENCY", "5"))
    TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "60"))
    RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", "3"))
    
    # Output Settings
    OUTPUT_DIR = "output"
    ASSETS_DIR = "assets"
    OUTPUT_FORMAT = "epub"  # 'epub' or 'pdf'

    # Batch Processing Settings
    BATCH_INPUT_DIR = "input/pipeline"
    BATCH_OUTPUT_DIR = "output/pipeline"

    
    # Translation Settings
    # For astronomy translation
    GLOSSARY_FILENAME = "astrodict241020_ec.txt"
    SYSTEM_PROMPT = """【Strict Instruction】
You are a professional translator specializing in Astronomy and Astrophysics.
Translate the following English text into professional Chinese.
Rules:
1. Output ONLY the translation. Do not include explanations, notes, or "Here is the translation".
2. Preserve all Markdown formatting (bold, italic, links, etc.) exactly.
3. Do not translate code blocks, math formulas (LaTeX), or image paths.
4. Use the following Glossary for consistency:
    - Red Shift -> 红移
    - Event Horizon -> 事件视界
    - Accretion Disk -> 吸积盘
    - Black Hole -> 黑洞
    - Neutron Star -> 中子星
    - White Dwarf -> 白矮星
    - Supernova -> 超新星
    - Dark Matter -> 暗物质
    - Dark Energy -> 暗能量
    - Big Bang -> 大爆炸
    - General Relativity -> 广义相对论
    - Special Relativity -> 狭义相对论
"""
    
#     ## For Java translation
#     GLOSSARY_FILENAME = None 
#     SYSTEM_PROMPT = """【Strict Instruction】  
# You are a professional translator specializing in Java programming and J2EE Enterprise Architecture.  
# Translate the following English text into professional Chinese.  
# Rules:  
# 1. Output ONLY the translation. Do not include explanations, notes, or "Here is the translation".  
# 2. Preserve all Markdown formatting (bold, italic, links, etc.) exactly.  
# 3. Do not translate code blocks, method names, variable names, or file paths. Keep them strictly in English.  
# 4. Use the following Glossary for consistency:  
#     - Dependency Injection (DI) -> 依赖注入  
#     - Inversion of Control (IoC) -> 控制反转  
#     - Aspect-Oriented Programming (AOP) -> 面向切面编程  
#     - Object-Relational Mapping (ORM) -> 对象关系映射  
#     - Garbage Collection (GC) -> 垃圾回收  
#     - Concurrency -> 并发  
#     - Multithreading -> 多线程  
#     - Interface -> 接口  
#     - Implementation -> 实现  
#     - Polymorphism -> 多态  
#     - Container -> 容器  
#     - Deployment -> 部署  
#     - Middleware -> 中间件  
#     - Microservices -> 微服务  
#     - Servlet -> Servlet (不翻译)  
#     - Bean -> Bean (不翻译)  
#     - Schema -> 模式  
#     - Transaction -> 事务  
# """  



    # Pipeline Step Configuration
    # Control which steps to execute in the pipeline
    PIPELINE_STEPS = {
        'prepare_paths': True,          # Step 0: Prepare paths and directories
        'pdf_to_markdown': True,         # Step 1: Convert PDF to Markdown
        'read_markdown': True,           # Step 2: Read Markdown file
        'parse_markdown': True,          # Step 3: Parse & chunk Markdown
        'identify_text_blocks': True,    # Step 4: Identify text blocks to translate
        'load_glossary': True,           # Step 4.1: Load glossary
        'translate': True,               # Step 5: Translate text blocks
        'merge_translations': True,      # Step 6: Merge translations back
        'reconstruct_markdown': True,    # Step 7: Reconstruct bilingual Markdown
        'generate_output': True          # Step 8: Generate Output (ePUB/PDF)
    }
    
    # Convenience presets for common workflows
    PIPELINE_PRESETS = {
        'prepare_only': ['prepare_paths', 'pdf_to_markdown', 'read_markdown', 'parse_markdown', 'identify_text_blocks'],
        'translate_only': ['load_glossary', 'translate', 'merge_translations'],
        'finalize_only': ['reconstruct_markdown', 'generate_output'],
        'all': list(PIPELINE_STEPS.keys())
    }
    
    # State file settings
    STATE_FILE_NAME = "pipeline_state.json"

    ORDERED_STEPS = [
        'prepare_paths',
        'pdf_to_markdown',
        'read_markdown',
        'parse_markdown',
        'identify_text_blocks',
        'load_glossary',
        'translate',
        'merge_translations',
        'reconstruct_markdown',
        'generate_output'
    ]

    @staticmethod
    def get_next_step(current_step):
        try:
            idx = Config.ORDERED_STEPS.index(current_step)
            if idx + 1 < len(Config.ORDERED_STEPS):
                return Config.ORDERED_STEPS[idx + 1]
        except ValueError:
            pass
        return None

    @staticmethod
    def get_headers():
        return {
            "Authorization": f"Bearer {Config.API_KEY}",
            "Content-Type": "application/json"
        }

    @staticmethod
    def get_payload(text, specific_glossary=None):
        system_prompt = Config.SYSTEM_PROMPT
        if specific_glossary:
            system_prompt += f"\n\nUse the following specific glossary for this section:\n{specific_glossary}"
            
        return {
            "model": Config.MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Original Text:\n{text}\n\nTranslation:"}
            ],
            "stream": False,
            "temperature": 0.1
        }
    
    @staticmethod
    def apply_preset(preset_name):
        """Apply a preset configuration to PIPELINE_STEPS."""
        if preset_name not in Config.PIPELINE_PRESETS:
            raise ValueError(f"Unknown preset: {preset_name}. Available: {list(Config.PIPELINE_PRESETS.keys())}")
        
        # Disable all steps first
        for step in Config.PIPELINE_STEPS:
            Config.PIPELINE_STEPS[step] = False
        
        # Enable only the steps in the preset
        for step in Config.PIPELINE_PRESETS[preset_name]:
            if step in Config.PIPELINE_STEPS:
                Config.PIPELINE_STEPS[step] = True
    
    @staticmethod
    def enable_steps(step_range):
        """Enable steps based on a range string like '0-4' or '5-7'."""
        # Map step numbers to step names
        step_map = {
            0: 'prepare_paths',
            1: 'pdf_to_markdown',
            2: 'read_markdown',
            3: 'parse_markdown',
            4: 'identify_text_blocks',
            5: 'translate',
            6: 'merge_translations',
            7: 'reconstruct_markdown',
            8: 'generate_output'
        }
        
        # Parse range (e.g., "0-4" or "5-7" or "8")
        if '-' in step_range:
            start, end = map(int, step_range.split('-'))
        else:
            start = end = int(step_range)
        
        # Disable all steps first
        for step in Config.PIPELINE_STEPS:
            Config.PIPELINE_STEPS[step] = False
        
        # Enable steps in range (note: step 4.1 is included with step 4)
        for i in range(start, end + 1):
            if i in step_map:
                Config.PIPELINE_STEPS[step_map[i]] = True
        
        # Special handling: if step 4 is enabled, also enable load_glossary
        if Config.PIPELINE_STEPS.get('identify_text_blocks'):
            Config.PIPELINE_STEPS['load_glossary'] = True
