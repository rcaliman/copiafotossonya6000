#!/usr/bin/python3

import os
import sys
from getpass import getuser
from datetime import datetime
from shutil import copy2
from PIL import Image

PATH_SDCARD = '/media/' + str(getuser()) + '/disk'
PATH_SERVIDOR = '/home/calmanet/arquivos/'
HTML_INDICE = PATH_SERVIDOR + 'indice_de_fotos.html'
TIPOS_DE_ARQUIVO = ['jpg', 'arw', 'mp4']


def busca_arquivos(_tipo: str, _local: str) -> list:
    """
    busca pelo tipo de arquivo na path especificada e retorna
    uma lista com a path completa de todos os arquivos desse tipo
    :param _tipo: str
    :param _local: str
    :return: list
    """
    lista_arquivos = []
    for conteudo_diretorios in os.walk(_local):
        path, _, *arquivos = conteudo_diretorios
        for arquivo in arquivos[0]:
            if f'.{_tipo.upper()}' in arquivo or f'.{_tipo.lower()}' in arquivo:
                lista_arquivos.append(str(path) + '/' + arquivo)
    return sorted(lista_arquivos, reverse=True)


def raw(_arquivo: str) -> str:
    """
    exibir o nome da versão raw do arquivo
    :param _arquivo: str
    :return: str
    """
    return _arquivo.replace('.JPG', '.ARW')


def data_de_criacao(_arquivo: str) -> str:
    """
    retorna a data de criação do arquivo
    :param _arquivo: str
    :return: str
    """
    stat = os.stat(_arquivo)
    data_arquivo = str(datetime.fromtimestamp(stat.st_mtime))[:10]
    return data_arquivo


def diretorio_destino(_arquivo) -> str:
    """
    retorna a path para onde serão copiados os arquivos para o servidor
    :param _arquivo: str
    :return: str
    """
    return PATH_SERVIDOR + data_de_criacao(_arquivo) + '/'


def arquivo_destino(_arquivo: str) -> str:
    """
    monta a path completa de destino do arquivo
    :param _arquivo: str
    :return: str
    """
    return diretorio_destino(_arquivo) + tipo_arquivo(_arquivo) + "/" + nome_arquivo(_arquivo)


def tipo_arquivo(_arquivo: str) -> str:
    """
    retorna o tipo do arquivo baseado na extensao
    :param _arquivo: str
    :return: str
    """
    return (_arquivo.rsplit('.')[1]).lower()


def nome_arquivo(_arquivo) -> str:
    """
    retira e retorna apenas o nome do arquivo da string da path
    :param _arquivo: str
    :return: str
    """
    return _arquivo.rsplit('/', 1)[1]


def copia_arquivo(_arquivo: str) -> None:
    """
    copia o arquivo do sdcard para o diretório no disco
    :param _arquivo: str
    :return: None
    """
    destino = diretorio_destino(_arquivo) + tipo_arquivo(_arquivo)
    copy2(_arquivo, destino)


def path_relativa(_arquivo: str) -> str:
    """
    extrai a path relativa de um arquivo
    :param _arquivo: str
    :return: str
    """
    return _arquivo.split('/')[-2] + '/' + _arquivo.split('/')[-1]


def path_absoluta(_arquivo: str) -> str:
    """
    extrai a path absoluta de um arquivo
    :param _arquivo: str
    :return: str
    """
    return _arquivo.rsplit('/', 1)[0]


def html_video(_arquivo: str) -> None:
    """
    cria o html para listar os videos no final do arquivo thumbs.html
    :param _arquivo: str
    :return: None
    """
    if os.path.isdir(diretorio_destino(_arquivo)):
        _arquivo_html = diretorio_destino(_arquivo) + 'thumbs.html'
        with open(_arquivo_html, 'a') as thumbs:
            thumbs.write(f"""
                    <div style='padding:15px;'>
                        <h3>VIDEO: 
                            <a href='mp4/{nome_arquivo(_arquivo)}'>
                                {nome_arquivo(_arquivo)}
                            </a>
                        </h3>
                    </div>
                """)


def diretorio_existe(_arquivo: str) -> bool:
    """
    retorna se o diretorio com a data do arquivo existe
    :param _arquivo:
    :return:
    """
    path_diretorio = PATH_SERVIDOR + data_de_criacao(_arquivo)
    return os.path.isdir(path_diretorio)


def cria_diretorios(_arquivo: str) -> None:
    """
    criar os diretórios para copiar os arquivos se eles não existirem
    :param _arquivo:
    :return: None
    """
    os.mkdir(diretorio_destino(_arquivo))
    os.mkdir(diretorio_destino(_arquivo) + 'thumbs')
    for tipo_de_arquivo in TIPOS_DE_ARQUIVO:
        os.mkdir(diretorio_destino(_arquivo) + tipo_de_arquivo)


def deleta_html_thumbs(_local_dos_arquivos: str) -> None:
    """
    apaga os arquivos html de thumbs para serem substituidos por arquivos atualizados
    :param _local_dos_arquivos: str
    :return: str
    """
    _arquivos = busca_arquivos('html', PATH_SERVIDOR)
    for _arquivo in _arquivos:
        if 'thumbs.html' in _arquivo:
            os.remove(_arquivo)


def cria_html_thumbs(_local_dos_arquivos: str, _nome_do_arquivo: str) -> None:
    """
    cria o html para exibir o conteudo dos diretorios criados
    :param _local_dos_arquivos: str
    :param _nome_do_arquivo: str
    :return: None
    """
    _arquivo_html = _local_dos_arquivos + 'thumbs.html'
    _arquivo_raw = _local_dos_arquivos + 'arw/' + raw(_nome_do_arquivo)
    _link_status = 'true'
    if os.path.isfile(_arquivo_raw):
        _link_status = 'true'
        _text_color = 'blue'
    else:
        _link_status = 'false'
        _text_color = 'white'
    with open(_arquivo_html, 'a') as _arquivo:
        _arquivo.write(f"""
                <div style='padding:15px;'>
                    <p>
                        <a style='text-decoration: none; color: blue;' href='jpg/{_nome_do_arquivo}'>
                            <strong style='font-family: "helvetica";font-size: 26px;'>
                                [ JPG ]
                            </strong>
                        </a>
                        &nbsp;&nbsp;
                        <a style='text-decoration: none; color: {_text_color};' onclick='return {_link_status};' href='arw/{raw(_nome_do_arquivo)}'>
                            <strong style='font-family: "helvetica";font-size: 26px;'>
                                [ RAW ]
                            </strong>
                        </a>
                    </p>
                    <a href='jpg/{_nome_do_arquivo}'>
                        <img src='thumbs/{_nome_do_arquivo}'>
                    </a>
                </div>
            """)


def cria_thumbs(_arquivo: str) -> None:
    """
    cria thumbnails dos arquivos .jpg
    :param _arquivo: str
    :return: None
    """
    if 'thumbs' not in _arquivo:  # previne que sejam criados thumbs dos thumbs
        tamanho_thumbs = 900, 900
        local_de_salvamento = diretorio_destino(_arquivo) + 'thumbs/'
        nome_de_salvamento = (_arquivo.rsplit('/', 1))[1]
        if not os.path.isfile(local_de_salvamento + nome_de_salvamento):  # nao recria os thumbs se eles já existem
            image = Image.open(_arquivo)
            image.thumbnail(tamanho_thumbs, 3)
            image.save(local_de_salvamento + nome_de_salvamento)
        cria_html_thumbs(diretorio_destino(_arquivo), nome_de_salvamento)


def executa_copia():
    """
    copia os arquivos do cartão de memoria para o HD
    :return: None
    """
    for tipo in TIPOS_DE_ARQUIVO:
        # para os tipos de arquivos declarados na lista no inicio do programa
        for _arquivo in busca_arquivos(tipo, PATH_SDCARD):
            # busca todos os arquivos dos tipos declarados na lista no inicio do programa
            if not diretorio_existe(_arquivo):
                # cria os diretorios relativo a data das fotos e os subdiretorios para os tipos de arquivos
                cria_diretorios(_arquivo)
                # copia os arquivos para seus respectivos diretorios
            if not os.path.isfile(arquivo_destino(_arquivo)):
                copia_arquivo(_arquivo)
                print(f'copiando arquivo {_arquivo}')
    print('FIM!')


def cria_index_html():
    """
    cria um arquivo de indice em html no diretorio principal listando todos os diretorios de foto abaixo dele
    :return: None
    """
    infos = ['', '']
    if os.path.isfile(HTML_INDICE):
        os.remove(HTML_INDICE)
    for _arquivo in (busca_arquivos('jpg', PATH_SERVIDOR)):
        cria_thumbs(_arquivo)
    for _arquivo in (busca_arquivos('mp4', PATH_SERVIDOR)):
        html_video(_arquivo)
    for _arquivo in (busca_arquivos('html', PATH_SERVIDOR)):
        if 'thumbs' in _arquivo:
            if os.path.isfile(path_absoluta(_arquivo) + '/info.txt'):
                infos.clear()
                with open(path_absoluta(_arquivo) + '/info.txt') as info:
                    for i in info:
                        infos.append(i.strip())
            with open(HTML_INDICE, 'a') as index:
                index.write(f"""
                <div>
                <table class='table table-bordered table-sm table-secondary table-striped mt-5'>
                    <tr>
                        <td><center>
                            <a style='text-decoration: none;'href={path_relativa(_arquivo)}>
                                {path_relativa(_arquivo).split('/')[0]} - {infos[0].upper()}
                            </a>
                        </td>
                    </tr>
                    <tr>
                        <td colspan=2>
                            {infos[1]}
                        </td>
                    </tr>
                    <tr>
                        <td colspan=2>
                        </td>
                    </tr>   
                </table>
                </div>      
                """)


def html_header():
    """
    cria um header para os arquivos html criados automaticamente
    :return: str
    """
    return """
        <html lang='pt-br'>
            <head>
                <meta charset="UTF-8" />
                <link rel='stylesheet' type='text/css' 
                    href='https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css'>
                <script type='text/javascript' 
                    src='https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.min.js'>
                </script>
            </head>
            <body>
                <div class='container d-flex justify-content-center'>
                <div class = 'w-75'>
    """


def html_footer():
    """
    cria um footer para os arquivos html criados automaticamente
    :return: str
    """
    return """
                    </div>
                </div>
            </body>
        </html>
    """


def formata_html(_arquivo):
    """
    aplica uma formatacao html com header e footer no arquivo html criado automaticamente.
    :param _arquivo: str
    :return: str
    """
    with open(_arquivo, 'r') as html_indice:
        html_indice_original = html_indice.read()
    with open(_arquivo, 'w') as html_indice_novo:
        html_indice_novo.write(html_header())
        html_indice_novo.write(html_indice_original)
        html_indice_novo.write(html_footer())


if len(sys.argv) > 1:
    if sys.argv[1] == 'indexar':
        deleta_html_thumbs(PATH_SERVIDOR)
        cria_index_html()
        formata_html(HTML_INDICE)
else:
    deleta_html_thumbs(PATH_SERVIDOR)
    executa_copia()
    cria_index_html()
    formata_html(HTML_INDICE)
