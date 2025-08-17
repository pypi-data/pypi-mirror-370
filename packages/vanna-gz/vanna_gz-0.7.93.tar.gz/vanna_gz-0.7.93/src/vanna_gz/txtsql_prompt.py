class TxtSqlPrompt:

    initial_prompt: str = ""
    question_sql_list: list
    ddl_list: list
    doc_list: list
    prompt: list = []

    def __init__(self, **kwargs):
        self.initial_prompt = kwargs.get("initial_prompt", "")
        self.question_sql_list = kwargs.get("question_sql_list", [])
        self.ddl_list = kwargs.get("ddl_list", [])
        self.doc_list = kwargs.get("doc_list", [])
        self.prompt = kwargs.get("prompt", [])
        self.prompt = kwargs.get("prompt", [])
