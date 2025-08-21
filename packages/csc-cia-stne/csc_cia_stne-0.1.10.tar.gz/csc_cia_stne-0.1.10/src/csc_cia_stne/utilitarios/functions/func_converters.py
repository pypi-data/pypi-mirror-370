def convert_bquery_result_to_json(query_result:list)->list:
    """Converte o resultado de uma query do BigQuery em uma lista de dicionários JSON

    Args:
        query_result (list): resultado da query do BigQuery (query.result)

    Returns:
        list: lista de dicionários JSON
    """
    
    try:
    
        #return [dict(row) for row in query_result]
        return [dict(row._asdict()) for row in query_result]
    
    except Exception as e:
    
        raise e
