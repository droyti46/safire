# =============================================================================
#  Safire Project - Library for testing of language models for jailbreaking
#
#  Description:
#      This module is part of the Safire project
#      It defines dataset loading utilities for prompt attacks testing
#
#  License:
#      This code is licensed under the MIT License.
#      See the LICENSE file in the project root for full license text.
#
#  Author:
#      Nikita Bakutov
# =============================================================================

import pandas as pd

from safire import constants

def load_adv_bench() -> pd.DataFrame:
    '''
    Load the AdvBench dataset containing adversarial prompts for testing

    Returns:
        pd.DataFrame: DataFrame with columns "prompt" and "target".
    '''
    df = pd.read_parquet(constants.ADV_BENCH_PATH)
    return df