from src.bpmn_neo4j.parsers.json_parser import load_json

class ParserFactory:
    @staticmethod
    def get_parser(file_path: str):
        if file_path.endswith(".json"):
            return JSONParser()
        raise ValueError("Unsupported file format")

class JSONParser:
    def parse(self, path):
        return load_json(path)
