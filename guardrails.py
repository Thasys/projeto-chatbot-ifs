import json
import os
from rapidfuzz import process, fuzz, utils


class Guardrails:
    def __init__(self, json_path="respostas_prontas.json"):
        self.data = self._load_data(json_path)
        self.knowledge_base = []

        # Prepara a base de conhecimento plana para busca rápida
        if self.data:
            for item in self.data:
                for trigger in item.get('gatilhos', []):
                    # Guarda tupla: (texto_gatilho, id_resposta)
                    self.knowledge_base.append((trigger, item['id']))

    def _load_data(self, path):
        if not os.path.exists(path):
            print(f"⚠️ [Guardrails] Arquivo {path} não encontrado.")
            return []
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(
                    f"🛡️ [Guardrails] Carregadas {len(data)} regras de interceptação.")
                return data
        except Exception as e:
            print(f"❌ [Guardrails] Erro no JSON: {e}")
            return []

    def check_intent(self, user_message):
        """
        Retorna a resposta pronta se a similaridade for alta.
        Retorna None se não houver match.
        """
        if not self.knowledge_base or not user_message:
            return None

        # 1. Normalização básica da entrada
        user_clean = str(user_message).lower().strip()

        # 2. Extrai apenas os textos dos gatilhos para o RapidFuzz comparar
        choices = [kb[0] for kb in self.knowledge_base]

        # 3. Busca o melhor match
        # token_set_ratio: Ótimo para quando as palavras estão fora de ordem ou há palavras extras
        # Ex: "Por favor qual a previsão para 2026" vs "Previsão 2026"
        result = process.extractOne(
            user_message,
            choices,
            scorer=fuzz.token_set_ratio,
            processor=utils.default_process
        )

        if result:
            match_text, score, index = result

            # 4. Definição de Limiar (Threshold)
            # 80 é um bom número: permite erros leves de digitação, mas evita falsos positivos
            LIMIT_SCORE = 80

            if score >= LIMIT_SCORE:
                matched_id = self.knowledge_base[index][1]
                print(
                    f"🛡️ [Guardrails] ATIVADO! Gatilho: '{match_text}' | Score: {score:.1f}")

                # Busca o texto da resposta pelo ID
                for item in self.data:
                    if item['id'] == matched_id:
                        return item['resposta']
            else:
                print(
                    f"🔍 [Guardrails] Ignorado. Melhor match: '{match_text}' ({score:.1f}%) < {LIMIT_SCORE}%")

        return None
