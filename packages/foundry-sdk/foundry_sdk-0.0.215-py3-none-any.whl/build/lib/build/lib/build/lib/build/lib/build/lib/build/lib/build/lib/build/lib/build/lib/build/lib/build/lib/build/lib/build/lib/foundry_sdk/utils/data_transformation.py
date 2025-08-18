import typing as t
import pandas as pd

def convert_to_df(relevant_cartegories: t.Dict[str, t.List[str]]) -> pd.DataFrame:
    """
    Converts a list of dictionaries to a pandas DataFrame.
    
    Parameters:
        data (List[Dict]): The list of dictionaries to convert.
        
    Returns:
        pd.DataFrame: The DataFrame created from the list of dictionaries.
    """

    category_relations = []
    for sub_category, parent_categories in relevant_cartegories.items():
        if parent_categories is None:
            category_relations.append({"subCategory": sub_category, "parentCategory": pd.NA})
        else:
            for parent_category in parent_categories:
                category_relations.append({"subCategory": sub_category, "parentCategory": parent_category})
    category_relations_df = pd.DataFrame(category_relations)

    return category_relations_df