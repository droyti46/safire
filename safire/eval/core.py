from typing import Callable, List, Dict, Optional, Any

import pandas as pd
from tqdm.notebook import tqdm
from IPython.display import HTML

from safire.eval.render import render_eval_summary

HTML('''
<style>
div.jp-OutputArea .progress {
    border-radius: 999px !important;
    overflow: hidden !important;
}
div.jp-OutputArea .progress-bar {
    background: linear-gradient(135deg, #02A0FF 0%, #130AFF 50%, #9934FF 100%) !important;
    transition: width 0.4s ease !important;
}
</style>
''')

def run_eval(
    model_fn: Callable[[Dict[str, str]], str],
    attacks: List[Dict[str, Any]],
    judge: Optional[Callable[[str], Any]] | None = None,
) -> pd.DataFrame:
    rows = []
    for attack in tqdm(attacks, 
                      desc="🧪 Running security evaluation",
                      unit="attack",
                      colour="#02A0FF"):
        messages = [{'role': role, 'content': content} 
                    for role, content in attack['attack_chat'].items()]

        response = model_fn(messages)

        if not isinstance(response, str):
            raise ValueError(f'Model function must return a string, but got {type(response).__name__}')

        row = {
            'attack_name': attack['attack_name'],
            'user_prompt': attack['user_prompt'],
            'attack_chat': attack['attack_chat'],
            'model_response': response,
        }

        if judge:
            row['result'] = judge(response)

        rows.append(row)

    df = pd.DataFrame(rows)
    render_eval_summary(df)
    return df