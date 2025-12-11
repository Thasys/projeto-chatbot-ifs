import pandas as pd

class DataTransformer:
    @staticmethod
    def clean_currency(val):
        if pd.isna(val): return 0.0
        val = str(val).strip()
        val = val.replace('.', '').replace(',', '.')
        if val.startswith('- '):
            val = '-' + val.replace('- ', '')
        return float(val)

    @staticmethod
    def split_cod_desc(text):
        if pd.isna(text) or ' - ' not in str(text):
            return str(text), str(text)
        parts = str(text).split(' - ', 1)
        return parts[0], parts[1]

    def processar(self, df_raw):
        if df_raw.empty:
            print("DataFrame vazio. Nada a transformar.")
            return None

        df = df_raw.copy()
        
        # Limpeza básica
        df.columns = df.columns.str.strip().str.replace('\ufeff', '')
        
        # Tratamento de Valor e Data
        df['valor_transacao'] = df['valor'].apply(self.clean_currency)
        
        # Identificar coluna de data dinamicamente ou usar 'data'
        col_data = 'data' if 'data' in df.columns else df.columns[0]
        df['data_emissao'] = pd.to_datetime(df[col_data], format='%d/%m/%Y', errors='coerce').dt.date

        # --- CRIAÇÃO DAS DIMENSÕES ---
        
        # 1. Dimensão Favorecido
        dim_favorecido = df[['codigoFavorecido', 'nomeFavorecido', 'ufFavorecido']].drop_duplicates().reset_index(drop=True)
        dim_favorecido['id_favorecido'] = dim_favorecido.index + 1

        # 2. Dimensão Programa
        cols_prog = ['funcao', 'subfuncao', 'programa', 'acao']
        temp_prog = df[cols_prog].drop_duplicates().reset_index(drop=True)
        for col in cols_prog:
            temp_prog[f'cod_{col}'], temp_prog[f'desc_{col}'] = zip(*temp_prog[col].map(self.split_cod_desc))
        
        dim_programa = temp_prog.drop(columns=cols_prog)
        dim_programa['id_programa'] = dim_programa.index + 1

        # 3. Dimensão Natureza
        cols_nat = ['categoria', 'grupo', 'modalidade', 'elemento']
        temp_nat = df[cols_nat].drop_duplicates().reset_index(drop=True)
        for col in cols_nat:
            temp_nat[f'cod_{col}'], temp_nat[f'desc_{col}'] = zip(*temp_nat[col].map(self.split_cod_desc))
            
        dim_natureza = temp_nat.drop(columns=cols_nat)
        dim_natureza['id_natureza'] = dim_natureza.index + 1

        # 4. Dimensão UG
        dim_ug = df[['codigoUg', 'ug', 'codigoOrgao', 'orgao']].drop_duplicates().reset_index(drop=True)
        dim_ug['id_ug'] = dim_ug.index + 1

        # --- CRIAÇÃO DA FATO ---
        fato = df.merge(dim_favorecido, on=['codigoFavorecido', 'nomeFavorecido', 'ufFavorecido'], how='left')
        fato = fato.merge(temp_prog.assign(id_programa=dim_programa['id_programa']), on=cols_prog, how='left')
        fato = fato.merge(temp_nat.assign(id_natureza=dim_natureza['id_natureza']), on=cols_nat, how='left')
        fato = fato.merge(dim_ug, on=['codigoUg', 'ug', 'codigoOrgao', 'orgao'], how='left')

        fato_final = fato[['data_emissao', 'documento', 'numeroProcesso', 'observacao', 
                           'id_favorecido', 'id_programa', 'id_natureza', 'id_ug', 'valor_transacao']]

        return {
            "dim_favorecido": dim_favorecido,
            "dim_programa": dim_programa,
            "dim_natureza": dim_natureza,
            "dim_ug": dim_ug,
            "fato_execucao": fato_final
        }