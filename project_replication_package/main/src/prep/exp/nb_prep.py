
#################################################
### THIS FILE WAS AUTOGENERATED! DO NOT EDIT! ###
#################################################
# file to edit: dev_nb/prep.ipynb

import json

import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split

def jsonl_df(file_list, columns, compression=None):
    """Load a list of jsonl.gz files into a pandas DataFrame."""
    return pd.concat([pd.read_json(f,
                                   orient='records',
                                   compression=compression,
                                   lines=True)[columns]
                      for f in file_list], sort=False)

def clean_html(post):
    """Removes all html tags that can occur inside a SO post."""
    result = re.sub(r"<.?span[^>]*>|<.?code[^>]*>|<.?p[^>]*>|<.?hr[^>]*>|<.?h[1-3][^>]*>|<.?a[^>]*>|<.?b[^>]*>|<.?blockquote[^>]*>|<.?del[^>]*>|<.?dd[^>]*>|<.?dl[^>]*>|<.?dt[^>]*>|<.?em[^>]*>|<.?i[^>]*>|<.?img[^>]*>|<.?kbd[^>]*>|<.?li[^>]*>|<.?ol[^>]*>|<.?pre[^>]*>|<.?s[^>]*>|<.?sup[^>]*>|<.?sub[^>]*>|<.?strong[^>]*>|<.?strike[^>]*>|<.?ul[^>]*>|<.?br[^>]*>", "", post)
    return result

def post_df(df):
    """Formats Dataframe from scrapped SO posts into query and res columns."""
    query = list(map('\n\n'.join, zip(df["q_body"], df["title"])))
    query = list(map(clean_html, query))
    res   = list(map(clean_html, df["a_body"]))
    new_df = pd.DataFrame({"query": query, "res": res})
    return new_df

def split_data(df):
    """Split DataFrame into training, validation, and testing sets."""
    df_trn, tmp = train_test_split(df, test_size = 0.2)
    df_val, df_tst = train_test_split(tmp, test_size = 0.5)

    return df_trn, df_val, df_tst

def split_causal_data(df, trn_splt = 0.8, val_splt = 0.1, tst_splt = 0.1):
    df_sz = len(df)
    trn_indx = int(df_sz * trn_splt)
    val_indx = int(df_sz * val_splt)

    df_trn = df.loc[:trn_indx]
    df_val = df.loc[(trn_indx + 1):(trn_indx + val_indx)]
    df_tst = df.loc[(trn_indx + val_indx + 1):]

    return df_trn, df_val, df_tst


def save_splits(dfs, output_path):
    """Save split of DataFrames into corresponding training, validation, and testing csv files."""
    dfs[0].to_csv(output_path/'trn.csv', index=False)
    dfs[1].to_csv(output_path/'val.csv', index=False)
    dfs[2].to_csv(output_path/'tst.csv', index=False)

def save_dfs(df, output_path):
    """Splits and saves a list of DataFrames to corresponding csv files in the output_path."""
    # split
    df_trn, df_val, df_tst = split_data(df)
    # Make sure the sizes match
    assert len(df) == (len(df_trn) + len(df_val) + len(df_tst))

    # save splits
    save_splits((df_trn, df_val, df_tst), output_path)

tags = {
    "mthds_cmts": "<$comment$>", "so_posts": "<$qa$>",
    "code_smell": "<$dirty$>", "buggy": "<$bug$>"
}
def tag_task(df, task_name):
    """Adds special tag to the end of the query based on the type of task."""
    new_query = list(map(lambda x: x + tags[task_name], df["query"]))
    df["query"] = pd.Series(new_query)

    return df

def read_data(path):
    """Read in the different data splits from some path."""
    df_trn = pd.read_csv(path/"trn.csv")
    df_val = pd.read_csv(path/"val.csv")
    df_tst = pd.read_csv(path/"tst.csv")

    return df_trn, df_val, df_tst

def tag_tasks(path):
    """Tag all tasks that exist in some path."""
    dfs = []
    for task_path in path.glob("*"):
        if task_path.stem == "merged": continue
        dfs.append(
            list(
                map(lambda x: tag_task(x, task_path.stem), read_data(task_path))
            )
        )

    return dfs

def merge_dfs(path, output):
    """Tag and merge tasks into a single DataFrame."""
    dfs = tag_tasks(path)
    merged_dfs = list(map(lambda x: pd.concat(x, ignore_index=True), zip(*dfs)))
    save_splits(merged_dfs, output)

    return merged_dfs