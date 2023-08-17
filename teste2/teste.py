import pandas as pd


df = pd.read_csv ('cpfs_consulta.csv')
update = df['data_nascimento'] == '01/01/1955'
update
df.loc[update, 'situacao_cadastral'] = 123
df.loc[update, 'data_inscricao'] = 123
df.loc[update, 'digito_verificador'] = 123
df.loc[update, 'ano_obito'] = 123
df.loc[update, 'data_hora_consulta'] = 123
df
print(df)