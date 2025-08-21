import requests
import PySimpleGUI as sg

from src import utils


def lable_oking(rotulo, tamanho=16, tamanho_texto=11, alinhamento='r'):
    # dots = NAME_SIZE-len(rotulo)-2  # + '•'*dots
    return sg.Text(rotulo, size=(tamanho, 1), justification=alinhamento, pad=(0, 0),
                   font=('Arial', tamanho_texto))  # Courier 10


def layout_aba(aba):
    return [
        [lable_oking('Status da Tarefa'), sg.Radio('Ligada', aba, key=f'-STATUS_{aba}_ON-', enable_events=True),
         sg.Radio('Desligada', aba, key=f'-STATUS_{aba}_OFF-', enable_events=True)],
        [sg.Text("Comando SQL", size=(16, 1), justification="r", pad=(0, 0), font=('Arial', 11,)),
         sg.Multiline(key=f'-SQL_{aba}-', font='Courier 12', pad=(10, 0), expand_x=True, expand_y=True)],
        [lable_oking("Intervalo"),
         sg.Multiline(key=f'-TEMPO_{aba}-', size=(6, 1), no_scrollbar=True, font='Courier 12', pad=(10, 0)),
         lable_oking('Intervalo em minutos entre cada execução.', 40, 12, 'l')],
        [lable_oking('Comentário'),
         sg.Multiline(key=f'-OBS_{aba}-', size=(60, 3), expand_x=True, font='Courier 12', pad=(10, 0))],
        # campos para testar

        [sg.Sizer(147, 0),
         sg.Button(' Salvar configurações ', key=f'-BTN_SAVE_{aba}-', pad=(10, 10)),
         # sg.Button(' Como usar (ajuda) ', key=f'BTN_VIDEO {aba}'),
         sg.Text('Clique aqui para orientações', key=f'LINK_VIDEO {aba}', enable_events=True,
                 font=('Arial', 12, 'underline'), text_color='blue')],

        [sg.Frame('Validar query', font='Arial 11', visible=True, key='-FRM_VALIDA-', size=(550, 60), layout=[
            [lable_oking('Linhas Retornadas:'),
             sg.Text(key=f'-RES_{aba}-', size=(4, 1), font='Courier 12'),
             sg.Push(), sg.pin(sg.Button('Validar Query ', key=f'-VALIDAR_{aba}-')), sg.Push(),
             sg.Push(), sg.pin(sg.Button('Executar JOB', key=f'-EXECJOB_{aba}-')), sg.Push(),
             sg.Push(), sg.pin(sg.Button('Query Final', key=f'-QUERY_FINAL_{aba}-')), sg.Push()
             ]
        ])],

    ]


sg.theme('Reddit')


# carrega configurações iniciais

# definições de layout
# layout_esquerda = [
#     [sg.Image(data=img_entrada)]
# ]
# layout_direita = [
#     [sg.Text(config["mensagem_titulo"],font=("Arial", 18),size=(36, 1),justification='center')],
#     [sg.Text(config["mensagem_entrada"],font=("Arial", 14),key='-MSG_ENTRADA-',
#     text_color='gray',size=(50,10),justification='center')],
#     [sg.Text('Informe o token de acesso',font=("Arial", 14), key='-TEXTO_TOKEN-')],
#     [sg.Text('Token: ',font=("Arial", 12), key='-LBL_TOKEN-'), sg.InputText('{token}}',
#     key="-TOKEN-", font=("Arial", 12))],
#     # campos que só serão exibidos depois da validação do token
#     [sg.Frame('Configurações de sua integração',font=('Arial 11'),key='-FRM_CONFIG-',layout=[
#         [lable_oking('Tipo do Banco'), sg.InputText(key="-BANCO-", size=(16,1),font=("Arial", 12))],
#         [lable_oking('Diretório'), sg.InputText(key="-DIR_DB-", size=(40), font=("Arial", 12))],
#         [lable_oking('Host ou IP'), sg.InputText(key="-HOST-", size=(16), font=("Arial", 12)),
#         lable_oking('Esquema',10), sg.InputText(key="-ESQUEMA-", size=(16), font=("Arial", 12))],
#         [lable_oking('Usuário'), sg.InputText(key="-USER_DB-", size=(16), font=("Arial", 12)),
#         lable_oking('Senha',10), sg.InputText(key="-PASS_DB-", size=(16), font=("Arial", 12))]
#     ])],
#     [sg.Push(), sg.Button('Entrar', key='-BTN_TOKEN-'),
#                 sg.Button('Salvar configurações',key='-BTN_CONFIG-', visible=False),
#                 sg.Button('Abrir Operações',key='-BTN_OPERACAO-', visible=False),
#                 sg.Button('Sair',key='-BTN_CANCEL-'),
#      sg.Push()]
# ]

def get_image(shortname, imagem):
    try:
        if shortname == '':
            return
        else:
            response = requests.get(f"https://{shortname}.oking.openk.com.br/api/consulta/configuracao")
            config = response.json()
            # faz download da imagem
            url_img = config[imagem]
            response = requests.get(url_img, stream=True)
            if response.status_code != 200:
                return
            response.raw.decode_content = True

            image = response.raw.read()
            return image
    except requests.ConnectionError as error:
        print(error)


def get_config_layout(shortname, mensagem):
    try:
        if shortname == '':
            return
        else:
            response = requests.get(f"https://{shortname}.oking.openk.com.br/api/consulta/configuracao")
            config = response.json()
            return config[mensagem]
    except requests.ConnectionError as error:
        print(error)


layout_shortname = [
    [sg.Text('Informe o Shortname de acesso', font=("Arial", 14), key='-TEXTO_SHORTNAME-')],
    [sg.Text('Shortname: ', font=("Arial", 12), key='-LBL_SHORTNAME-'),
     sg.InputText('', key="-SHORTNAME-", font=("Arial", 12))],
    [sg.Push(), sg.Button('Salvar', key='-BTN_SALVAR-'), sg.Button('Sair', key='-BTN_EXIT-')]
]

layout_erroconexao = [
    [sg.Text('Erro de conexão', font=("Arial", 12), key='-TEXTO_ERROCONEXAO-', text_color='red')],
    [sg.Push(), sg.Button('Continuar', key='-BTN_TENTAR-'),
     sg.Button('Sair', key='-SAIR-', button_color='red'), sg.Push()]
]

# image_connection = [
#     [sg.Image(get_image(config_shortname, "imagem_entrada"), key = '-IMAGEM-')]
# ]


connection_direita = [[sg.Text((get_config_layout('', "mensagem_titulo")), font=("Arial", 18), key='-MSG_TITULO-',
                               size=(36, 1), justification='center')],
                      [sg.Text(get_config_layout('', "mensagem_entrada"), font=("Arial", 14), key='-MSG_ENTRADA-',
                               text_color='gray',
                               size=(50, 10), justification='center')],
                      [sg.Frame('Configurações de sua integração', font='Arial 11', key='-FRM_CONFIG-', layout=[
                          [lable_oking('Tipo do Banco'), sg.InputText(key="-BANCO-", size=(16, 1), font=("Arial", 12))],
                          [lable_oking('Diretório'), sg.InputText(key="-DIR_DB-", size=40, font=("Arial", 12))],
                          [lable_oking('Host ou IP'), sg.InputText(key="-HOST-", size=16, font=("Arial", 12)),
                           lable_oking('Esquema', 10), sg.InputText(key="-ESQUEMA-", size=16, font=("Arial", 12))],
                          [lable_oking('Usuário'), sg.InputText(key="-USER_DB-", size=16, font=("Arial", 12)),
                           lable_oking('Senha', 10), sg.InputText(key="-PASS_DB-", size=16, font=("Arial", 12))],
                          [sg.Push(),
                           sg.Button('Salvar configurações', key='-BTN_CONFIG-'),
                           sg.Button('Abrir Operações', key='-BTN_OPERACAO-'),
                           sg.Button('Sair', key='-BTN_CANCEL-'),
                           sg.Push()]]
                                )]]

layout_change_token = [[lable_oking('Selecione o Token:', 60, 16, 'l')],
                       [sg.Frame('Opções do Token', font='Arial 11', visible=True, key='-FRM_EDIT_TOKEN-',
                                 layout=[[sg.Combo(values=[], key="-COMBO_TOKEN-", size=(100, 10), readonly=True)],
                                         [sg.Button('Selecionar', key='-BTN_ESCOLHER_TOKEN-'),
                                          sg.Button('Novo Token', key='-BTN_NOVO_TOKEN-'),
                                          sg.Push(), sg.Button('Voltar', key='-BTN_VOLTAR_TOKEN-')]])]]

layout_conection = [
    [sg.Column([[sg.Image(get_image('', "imagem_entrada"), key='-IMG_ENTRADA-')]]),
     sg.VerticalSeparator(color='gray', pad=1), sg.Column(connection_direita)]
]

# image_token = [
#     [sg.Image(get_image(config_shortname, "imagem_entrada"))]
# ]

# token_direita = [
#     [sg.Text(get_config_layout('', "mensagem_titulo"), font=("Arial", 18), size=(36, 1), justification='center')],
#     [sg.Text(get_config_layout('', "mensagem_entrada"), font=("Arial", 14), key='-MSG_ENTRADA-',
#     text_color='gray', size=(50, 10),
#              justification='center')],
#     [sg.Text('Informe o token de acesso', font=("Arial", 14), key='-TEXTO_TOKEN-')],
#     [sg.Text('Token: ', font=("Arial", 12), key='-LBL_TOKEN-'),
#      sg.InputText('', key="-TOKEN-",
#                   font=("Arial", 12))],
#     [sg.Push(),
#      sg.Button('Entrar', key='-BTN_TOKEN-'),
#      sg.Button('Sair', key='-BTN_CANCEL-'),
#      sg.Push()]
# ]

layout_token = [
    [sg.Column([[sg.Image(get_image('', "imagem_entrada"), key='-IMAGEM-')]]),
     sg.VerticalSeparator(color='gray', pad=1), sg.Column([
        [sg.Text(get_config_layout('', "mensagem_titulo"), font=("Arial", 18), key='-MSG_TITULO-', size=(36, 1),
                 justification='center')],
        [sg.Text(get_config_layout('', "mensagem_entrada"), font=("Arial", 14), key='-MSG_ENTRADA-', text_color='gray',
                 size=(50, 10),
                 justification='center')],
        [sg.Text('Informe o nome que deseja para essa integração (a sua escolha)', font=("Arial", 14),
                 key='-TEXTO_NOME-')],
        [sg.Text('Nome: ', font=("Arial", 12), key='-LBL_NOME-'),
         sg.InputText('', key="-NOME-",
                      font=("Arial", 12))],
        [sg.Text('Informe o token de acesso', font=("Arial", 14), key='-TEXTO_TOKEN-')],
        [sg.Text('Token: ', font=("Arial", 12), key='-LBL_TOKEN-'),
         sg.InputText('', key="-TOKEN-",
                      font=("Arial", 12))],
        [sg.Push(),
         sg.Button('Entrar', key='-BTN_TOKEN-'),
         sg.Button('Sair', key='-BTN_CANCEL-'),
         sg.Push()]
        ])
     ]
]

layout_new_token = [[lable_oking('Nova Conexão', 45, 16, 'l')],
                    [sg.Frame('Dados do Token', font='Arial 11', visible=True, key='-FRM_TOKEN-',
                              layout=[[sg.Text('Informe o nome que deseja para essa integração (a sua escolha)',
                                               font=("Arial", 14),
                                               key='-TEXTO_NOME-')],
                                      [sg.Text('Nome: ', font=("Arial", 12), key='-LBL_NOME-'),
                                       sg.InputText('', key="-NOME-", font=("Arial", 12))],
                                      [sg.Text('Informe o novo token de acesso', font=("Arial", 14),
                                               key='-TEXTO_TOKEN-')],
                                      [sg.Text('Token: ', font=("Arial", 12), key='-LBL_TOKEN-'),
                                       sg.InputText('', key="-TOKEN-",
                                                    font=("Arial", 12))]])],
                    [sg.Push(),
                     sg.Button('Criar', key='-BTN_NOVO_TOKEN-'),
                     sg.Button('Voltar', key='-BTN_CANCEL-'),
                     sg.Push()]]

""" substituido pela função layout_aba
aba_estoque = [
    [lable_oking('Comando SQL'), sg.Multiline(key='-SQL_ESTOQUE-', size=(60, 15),font=('Courier 12'))],
    [lable_oking('Intervalo'), sg.InputText(key='-TEMPO_ESTOQUE-', size=(6),font=('Courier 12')), 
    lable_oking('Intervalo em minutos entre cada execução.',40,12,'l')],
    [lable_oking('Comentário'), sg.Multiline(key='-OBS_ESTOQUE-', size=(60, 5),font=('Courier 12'))],
    [sg.Push(),sg.Button(' Salvar configurações ', key='-BTN_ESTOQUE-'),sg.Push()]
]
aba_preco = [
    [lable_oking('Comando SQL'), sg.Multiline(key='-SQL_PRECO-', size=(60, 15), font=('Courier 12'))],
    [lable_oking('Intervalo'), sg.InputText(key='-TEMPO_PRECO-', size=(6),font=('Courier 12')),
    lable_oking('Intervalo em minutos entre cada execução.',40,12,'l')],
    [lable_oking('Comentário'), sg.Multiline(key='-OBS_PRECO-', size=(60, 5),font=('Courier 12'))],
    [sg.Push(),sg.Button(' Salvar configurações ', key='-BTN_PRECO-'),sg.Push()]
]
aba_pedido = [
    [lable_oking('Comando SQL'), sg.Multiline(key='-SQL_PEDIDO-', size=(60, 15),font=('Courier 12'))],
    [lable_oking('Intervalo'), sg.InputText(key='-TEMPO_PEDIDO-', size=(6),font=('Courier 12')),
    lable_oking('Intervalo em minutos entre cada execução.',40,12,'l')],
    [lable_oking('Comentário'), sg.Multiline(key='-OBS_PEDIDO-', size=(60, 5),font=('Courier 12'))],
    [sg.Push(),sg.Button(' Salvar configurações ', key='-BTN_PEDIDO-'),sg.Push()]
]
aba_notafiscal = [
    [lable_oking('Comando SQL'), sg.Multiline(key='-SQL_NOTAFISCAL-', size=(60, 15), font=('Courier 12'))],
    [lable_oking('intervalo'), sg.InputText(key='-TEMPO_NOTAFISCAL-', size=(6),font=('Courier 12')),
    lable_oking('Intervalo em minutos entre cada execução.',40,12,'l')],
    [lable_oking('Comentário'), sg.Multiline(key='-OBS_NOTAFISCAL-', size=(60, 5),font=('Courier 12'))],
    [sg.Push(),sg.Button(' Salvar configurações ', key='-BTN_NOTAFISCAL-'),sg.Push()]
]
"""

# layout_html = [[]]

layout_criar_db = [[lable_oking('Criar Banco de Dados', 80, 12, 'c')],
                   [lable_oking('Comando'), sg.Multiline(key='-CREATE_DB-', size=(60, 12), font='Courier 12')],
                   [sg.Frame('Permissão', font='Arial 11', visible=True, key='-FRM_CREATE-', size=(500, 120),
                             layout=[
                                 [lable_oking('Usuário'), sg.InputText(key='-USER-', size=16, font='Courier 12')],
                                 [lable_oking('Senha'),
                                  sg.InputText(key='-PASSWORD-', size=16, font='Courier 12', password_char='*')],
                                 [sg.Push(), sg.Button('Criar', key='-BTN_CREATE-'), sg.Push()]])]]

layout_query_final = [[sg.Text('Query Final:', font=("Arial", 12)),
                       sg.Multiline(key='-QUERY_FINAL-', expand_x=True, expand_y=True,
                                    font='Courier 12', disabled=True,
                                    background_color='#F5F5F5', pad=(10, 10))]]

layout_logs = [[sg.Text('Logs', key='-TITLE_LOGS-'), sg.Combo([], key="-COMBO_LOGS-", readonly=True, enable_events=True,
                                                              pad=(0, 0), size=(15, 10))],
               [sg.Table(headings=['Tarefa', 'Identificador', 'Tipo', 'Mensagem',
                                   'Ocorrências', 'Primeira Ocorrência',
                                   'Última Ocorrência'], col_widths=[10, 5, 0, 30, 3, 8, 8],
                         values=[], expand_x=True, expand_y=True, enable_events=True,
                         justification='left', auto_size_columns=False, enable_click_events=True,
                         key='-TABLE_LOGS-', font=('Arial', 8))]]

tabela_fotos = [[sg.Table(headings=['Fotos Pendentes'], key="-FOTOSPEND-", values=[], expand_x=True, expand_y=True,
                          justification='left')]]
tabela_processadas = [[sg.Table(headings=['Fotos Processadas'], key="-FOTOSPROC-", values=[], expand_x=True,
                                expand_y=True, justification='left')]]

layout_foto_mass = [[sg.Text('Arquivo'), sg.In(size=(50, 1), readonly=True, key='-FOLDER-', enable_events=True),
                     sg.FolderBrowse(key='-FILES-')],
                    [sg.Column(tabela_fotos, expand_x=True, expand_y=True),
                     sg.Column(tabela_processadas, expand_x=True, expand_y=True)],
                    [sg.Button('Enviar', key='-ENVIARFOTOS-', pad=(10, 10)),
                     sg.Text('Pendentes: '),
                     sg.InputText('', key='-PENDENTES-', border_width=0, readonly=True,
                                  size=5, background_color=sg.theme_background_color()), sg.Push(),
                     sg.Text('Processadas: '),
                     sg.InputText('', key='-PROCESSADAS-', border_width=0, readonly=True,
                                  size=5, background_color=sg.theme_background_color()), sg.Push()]]


def tab_group_layout(dict_abas):
    lista = [sg.Tab('Operaçoes', layout=[[sg.Column(layout=[[sg.Frame(layout=[], key='-FRAME_DASHBOARD-',
                                                                      expand_x=True, expand_y=True, title='',
                                                                      border_width=0)]], expand_y=True, expand_x=True,
                                                    scrollable=True, vertical_scroll_only=True,
                                                    key='-COLUMN_DASHBOARD-')]],
                    visible=True, key='-ABA_DASHBOARD-', element_justification='top'),
             sg.Tab('Logs', layout_logs, visible=False, key='-ABA_LOGS-', expand_x=True, expand_y=True),
             sg.Tab('Novo banco de dados', layout_criar_db, key='-ABA_NOVO_BD-', visible=False),
             sg.Tab('Query Final', layout_query_final, key="-TAB_QUERY_FINAL-", visible=False),
             sg.Tab('Enviar fotos', layout_foto_mass, key="-ABA_FOTOSMASS-", visible=False)
             ]
    for aba in dict_abas.values():
        lista.append(
            sg.Tab(aba['job_description'], layout_aba(aba['job_type']), visible=False, key=f'-ABA_{aba["job_type"]}-'))
    return sg.TabGroup([lista], key="-TAB_GROUP-", pad=(10, 0), expand_x=True, expand_y=True)


layout_operacao = [
    [sg.Frame(key='-FRAME_OPERACAO-', title='', expand_x=True, expand_y=True, pad=(0, 0), border_width=0, layout=[
        [sg.Image(get_image('', "logo"), key='-IMG_LOGO-', pad=10),
         sg.Text('', pad=((0, 0), (0, 3)), font=('Arial', 14), key="-MSG_TOKEN-"),
         sg.Text('', text_color='#0178d2', font=('Arial', 10, 'bold'),
                 key="-TOKEN_ATUAL-")],
        [sg.Sizer(20, 0), lable_oking('Operações de sua integração', 60, 16, 'l')],
        [sg.Frame('', expand_x=True, border_width=0, pad=(0, 10), background_color='#0178d2', size=(0, 24),
                  key='-OPERACOES_FRAME-',
                  layout=[[sg.Button('Dashboard', key="-DASHBOARD-", pad=(0, 0), border_width=0),
                           sg.ButtonMenu('Catálogo', menu_def=['', []], key="-DROP_MENU_CATALOGO-", pad=(0, 0),
                                         border_width=0, visible=False),
                           sg.ButtonMenu('Pedido', menu_def=['', []], key="-DROP_MENU_PEDIDO-", pad=(0, 0),
                                         border_width=0, visible=False),
                           sg.ButtonMenu('Auxiliares', menu_def=['', []], key="-DROP_MENU_AUX-", pad=(0, 0),
                                         border_width=0, visible=False),
                           sg.ButtonMenu('Configuração', menu_def=['', ['Integração', 'Token', 'Setup (Create)']],
                                         key="-DROP_MENU_CONFIG-", visible=False,
                                         pad=(0, 0), border_width=0),
                           sg.Button('Enviar Fotos', key="-FOTOSMASS-", pad=(0, 0), border_width=0)]])],
        [tab_group_layout(utils.dict_all_jobs)],
        [sg.Text('', key="-VERSAO-", pad=(10, 5)), sg.Button('           ', key="-KEY_PYSIMPLEGUI-", pad=(0, 0),
                                                             border_width=0, button_color="white"),
         sg.Push(), sg.Button('Fechar', key='-BTN_FECHAR-', pad=(10, 10))]
    ])]]


def tabela_dashboard(tarefa, tempo, medida, ultima_execucao, largura, cor):
    edit_button = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA9AAAAPQBFLZpEgAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAIMSURBVEiJrdY/bE5hFAbw360iSPwbJGKpgcRQSw1MJCy6GPhSEaY2ERZTB5ZGMAuhja4klSCV+LMhqahYOjQ2ooKIdGproFRfwz1tr0+/L/dr+iYn977Pe97znPPcc+97pZQsh2ENruMbXqMzpWS5gq/CM6Qqa8/CQZZlu3AKbdig/viDGymlgSzLmnAXFUyhAztxDUNzGXThxyIZ1LOHsbc35j9xILBjgT3NsCc0a8YIbuFTiQqG0Y2emFdSSoNZlrViCBtxAu4F26MGdT9bqKYrsO34GtiTSNr7ANobCF6JrBPOB7YF7wJ7hbVzz3ciwJaSwQ9iOvZcDWx9yJvwFpsK/uUJ5B02Ff63kWE1XgT2Eduq9pQjwA6MV+m7Ag8CG5e352G0NUSArRgLv+GCvv2BfZd342bMYKw0QbTbaLW+uBLYNA4F1hLYRCkCrMTLQjt2B34u5nP9b6kEHbH2q0AygNm4P1Pl3zDB/Vi7jEsFkoSeRfz/I2hSY2RZti46At7IP8e/Y96bUrpYa2/1WLQCHC1kO1O4v4OmGg1RvgJ5j88XhEHsTymdTCnNls2+uc7aY1yQnw39KaUPZYNWjy/ysvY28jWtIdG+iPW5KNFoEHUuNcPCOB3XkSJYsXAi3USrXJZGbDf6LLwvR+aritL6NHZc1rPef2Qr6HcczzG5hKCT8r+KSvVz+QsltfhWTWGwDgAAAABJRU5ErkJggg==/a1RBFAXwn65GESGKrJUQSWESFT+AnYgRLAXBb5BOs2oU7U1jG4iNrQpiY2mjRBHEYLVNEgJJY0gV/4OCicXc4PJ2d/a9sB4YeMycOffMvHvv8J+xqyTvKoYKc6t42i8jTWwVRrNf4q14FaM0aiV5xzGOyxjEOr7jS5VgnXABb7Gp/Yo28QbngzuKJ6iXER7AbAgtYRInsQ974vsGloPzCJ+whiO9xGt4Fg7vR7Bu2Ivp4P7CWBn3d8LV9Q5rEzGKaMSea73Ej+KndIJOyGXRc+mnH84FuIc/OLGDACPSVTVaJ3cXSBfxAYs5F12wgHlcygU4HaSdYl7KsK4BBrGREfgWJka7rG/gUC7AZ/mfdAu/8RqnOqzX8TWz3xze5wiS+zWpAIv4iJe5zXelTBjpEWQYVwpzY1ItNNrp/1DHDymnq+KFVAc9W8VUOJmsIH5bCffbaO1F0/K9aD8ehPhj5V9IA3gYG5dxU0rPAziIM1LPWg3OjNRlK2Mc77S/BdvvwRzO5QTKHmkIZ3FMqp0VKZ1XqnvuM/4C7Rlj3t5Q924AAAAASUVORK5CYII= '
    stop_watch = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAsQAAALEBxi1JjQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAGhSURBVEiJtdU/a1RBFAXwn65GESGKrJUQSWESFT+AnYgRLAXBb5BOs2oU7U1jG4iNrQpiY2mjRBHEYLVNEgJJY0gV/4OCicXc4PJ2d/a9sB4YeMycOffMvHvv8J+xqyTvKoYKc6t42i8jTWwVRrNf4q14FaM0aiV5xzGOyxjEOr7jS5VgnXABb7Gp/Yo28QbngzuKJ6iXER7AbAgtYRInsQ974vsGloPzCJ+whiO9xGt4Fg7vR7Bu2Ivp4P7CWBn3d8LV9Q5rEzGKaMSea73Ej+KndIJOyGXRc+mnH84FuIc/OLGDACPSVTVaJ3cXSBfxAYs5F12wgHlcygU4HaSdYl7KsK4BBrGREfgWJka7rG/gUC7AZ/mfdAu/8RqnOqzX8TWz3xze5wiS+zWpAIv4iJe5zXelTBjpEWQYVwpzY1ItNNrp/1DHDymnq+KFVAc9W8VUOJmsIH5bCffbaO1F0/K9aD8ehPhj5V9IA3gYG5dxU0rPAziIM1LPWg3OjNRlK2Mc77S/BdvvwRzO5QTKHmkIZ3FMqp0VKZ1XqnvuM/4C7Rlj3t5Q924AAAAASUVORK5CYII= '
    comment = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAsQAAALEBxi1JjQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAEMSURBVEiJ1dW9SgNBFIbhJ2sghWDAxkLIPcRKEVJ5AYKVP5WFoKAX4SV4E1aCYGsS7ETBUnsJdlZqYRMtMsFENnFHZws/OMxy2P3es2fPzlCyKmGdxRbmE/k+4xRvUMUtPhLHTfDWDIn9RNXDQfBsZqiH5ENCwH1Y61lC01yVDqhOyK+gFel1heuigE0cRgJOYgBHIf6s37QotxWxgGktym1FLCBZi/7/f5ChH65nEvoOvfoVLOARdzgfuen7tNSwi7kCgHUsoTFM7KBnfLu9HHlgMcCKbtU9bE+roBsCVvGEF2wUqH5MP33kPXTwimWcxQImqYt3g9e98HVmJFPbYLqOlTTKLayVYZxcn0ncTO6mOygsAAAAAElFTkSuQmCC/a1RBFAXwn65GESGKrJUQSWESFT+AnYgRLAXBb5BOs2oU7U1jG4iNrQpiY2mjRBHEYLVNEgJJY0gV/4OCicXc4PJ2d/a9sB4YeMycOffMvHvv8J+xqyTvKoYKc6t42i8jTWwVRrNf4q14FaM0aiV5xzGOyxjEOr7jS5VgnXABb7Gp/Yo28QbngzuKJ6iXER7AbAgtYRInsQ974vsGloPzCJ+whiO9xGt4Fg7vR7Bu2Ivp4P7CWBn3d8LV9Q5rEzGKaMSea73Ej+KndIJOyGXRc+mnH84FuIc/OLGDACPSVTVaJ3cXSBfxAYs5F12wgHlcygU4HaSdYl7KsK4BBrGREfgWJka7rG/gUC7AZ/mfdAu/8RqnOqzX8TWz3xze5wiS+zWpAIv4iJe5zXelTBjpEWQYVwpzY1ItNNrp/1DHDymnq+KFVAc9W8VUOJmsIH5bCffbaO1F0/K9aD8ehPhj5V9IA3gYG5dxU0rPAziIM1LPWg3OjNRlK2Mc77S/BdvvwRzO5QTKHmkIZ3FMqp0VKZ1XqnvuM/4C7Rlj3t5Q924AAAAASUVORK5CYII= '
    color = sg.theme_input_background_color() if cor else sg.theme_background_color()
    return [[sg.Frame(key=f'-FRAME_GERAL_{tarefa}-', border_width=0, pad=(0, 0), expand_x=True, size=(0, 40), title='',
                      layout=[
                          [sg.Frame(key=f'-FRAME_EDIT_{tarefa}-', background_color=color, border_width=0,
                                    size=(int(largura / 4), 0),
                                    expand_y=True, title='',
                                    layout=[[sg.Sizer(6, 6)],
                                            [sg.Text(tarefa, background_color=color, key=f'-TEXT_EDIT_{tarefa}-'),
                                             sg.Push(background_color=color),
                                             sg.Button(image_data=edit_button,
                                                       key=f'-EDIT_BTN_{tarefa}-',
                                                       border_width=0, button_color=color),
                                             sg.Sizer(5, 0)]]),
                           sg.Frame(key=f'-FRAME_TEMPO_{tarefa}-', border_width=0, size=(int(largura / 6), 0),
                                    expand_y=True, title='',
                                    background_color=color,
                                    layout=[[sg.Sizer(6, 6)],
                                            [sg.Sizer(5, 0), sg.Image(data=stop_watch, background_color=color),
                                             sg.Text(f'{tempo} em {tempo} {medida}', background_color=color,
                                                     key=f'-INFO_TEMPO_{tarefa}-')]]),
                           sg.Frame(key=f'-FRAME_LOG_{tarefa}-', border_width=0, size=(int(largura / 18), 0),
                                    expand_y=True, title='',
                                    element_justification='center',
                                    background_color=color,
                                    layout=[[sg.Sizer(6, 6)], [sg.Image(data=comment, background_color=color),
                                                               sg.Text('LOG', key=f'-LOG_BTN_{tarefa}-',
                                                                       enable_events=True,
                                                                       font=('Arial', 12, 'underline'),
                                                                       text_color='blue',
                                                                       background_color=color)]]),
                           sg.Frame(key=f'-FRAME_ULT_{tarefa}-', border_width=0, size=(int(largura / 1.6), 0),
                                    expand_y=True, title='',
                                    background_color=color,
                                    layout=[[sg.Sizer(6, 6)], [sg.Image(data=stop_watch, background_color=color),
                                                               sg.Text(ultima_execucao, background_color=color,
                                                                       key=f'-INFO_ULT_{tarefa}-')]])]])]]
