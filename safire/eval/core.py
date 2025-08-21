import pandas as pd
from typing import Callable, List, Dict, Optional, Any

def run_eval(
    model_fn: Callable[[Dict[str, str]], str],
    attacks: List[Dict[str, Any]],
    judge: Optional[Callable[[str], Any]] | None = None,
) -> pd.DataFrame:
    rows = []
    for attack in attacks:
        response = model_fn(attack['attack_chat'])
        row = {
            'attack_name': attack['attack_name'],
            'user_prompt': attack['user_prompt'],
            'attack_chat': attack['attack_chat'],
            'model_response': response,
        }

        if judge:
            row['result'] = judge(response)

        rows.append(row)

    return pd.DataFrame(rows)