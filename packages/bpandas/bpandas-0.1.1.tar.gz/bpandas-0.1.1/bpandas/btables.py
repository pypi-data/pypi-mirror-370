import pandas as pd


def bfrequencies(
    df: pd.DataFrame,
    column_name: str,
    *,
    include_na: bool = True,
    sort_by: str = "index",  # "index" ou "count"
    ascending: bool = True,
    percent: bool = True,  # True = retorna %; False = proporção 0–1
    decimals: int = 2,
) -> pd.DataFrame:
    """
    Gera uma tabela de distribuição de frequências para uma coluna do DataFrame.

    Args:
        df (pd.DataFrame): DataFrame de entrada.
        column_name (str): Nome da coluna a ser analisada.
        include_na (bool, opcional): Se True, inclui valores NaN/None na contagem.
            Padrão True.
        sort_by (str, opcional): Como ordenar a distribuição.
            "index" = ordena pelo valor único (rótulo) da coluna.
            "count" = ordena pela frequência absoluta.
            Padrão "index".
        ascending (bool, opcional): Ordem crescente (True) ou decrescente (False).
            Padrão True.
        percent (bool, opcional): Se True, retorna frequência relativa em porcentagem (0–100).
            Se False, retorna proporção (0–1). Padrão True.
        decimals (int, opcional): Casas decimais para arredondar a frequência relativa.
            Padrão 2.

    Returns:
        pd.DataFrame: DataFrame com colunas:
            - value: valor distinto da coluna analisada
            - frequency: frequência absoluta
            - relative_frequency: frequência relativa (% ou proporção)
            - cumulative_frequency: frequência absoluta acumulada
            - cumulative_relative_frequency: frequência relativa acumulada

    Exemplo:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"sexo": ["M","F","M","M","F", None]})
        >>> table_distribution_maker(df, "sexo")
          value  frequency  relative_frequency  cumulative_frequency  cumulative_relative_frequency
        0     F          2               33.33                     2                        33.33
        1  None          1               16.67                     3                        50.00
        2     M          3               50.00                     6                       100.00
    """
    # 1) Frequência absoluta
    s = df[column_name].value_counts(
        dropna=not include_na, sort=False
    )  # sem ordenar aqui

    # 2) Ordenação
    if sort_by == "index":
        s = s.sort_index(ascending=ascending)
    elif sort_by == "count":
        s = s.sort_values(ascending=ascending)
    else:
        raise ValueError('sort_by deve ser "index" ou "count".')

    # 3) Frequência relativa (proporção ou %)
    rel = s / s.sum()
    if percent:
        rel = (rel * 100).round(decimals)
    else:
        rel = rel.round(decimals)

    # 4) Acumuladas
    cum = s.cumsum()
    cum_rel = rel.cumsum().round(decimals)

    # 5) Montagem do DataFrame de retorno
    out = pd.DataFrame(
        {
            "value": s.index,
            "frequency": s.values,
            "relative_frequency": rel.values,
            "cumulative_frequency": cum.values,
            "cumulative_relative_frequency": cum_rel.values,
        }
    ).reset_index(drop=True)

    return out
