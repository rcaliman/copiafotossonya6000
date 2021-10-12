#!/usr/bin/python3

import os
from getpass import getuser
from datetime import datetime
from shutil import copy2
from PIL import Image


PATH_SDCARD = '/media/' + str(getuser()) + '/disk'
PATH_SERVIDOR = '/home/calmanet/arquivos/'
TIPOS_DE_ARQUIVO = ['jpg', 'arw', 'mp4']


def busca_arquivos(_tipo: str) -> list:
    """path_sdcard = '/media/' + str(getuser()) + '/disk'
    busca pelo tipo de arquivo na path especificada e retorna
    uma lista com a path completa de todos os arquivos desse tipo
    :param _tipo: str
    :return: list
    """
    lista_arquivos = []
    for conteudo_diretorios in os.walk(PATH_SDCARD):
        path, _, *arquivos = conteudo_diretorios
        for arquivo in arquivos[0]:
            if f'.{_tipo.upper()}' in arquivo or f'.{_tipo.lower()}' in arquivo:
                lista_arquivos.append(str(path) + '/' + arquivo)
    return lista_arquivos


def busca_arquivos_anteriores() -> list:
    """
    retorna a lista de arquivos que já haviam no servidor para o sistema saber o que não copiar
    :return: list
    """
    _lista_arquivos_anteriores = []
    for arquivos_anteriores in os.walk(PATH_SERVIDOR):
        path, _, *_arquivos = arquivos_anteriores
        _lista_arquivos_anteriores.extend(_arquivos[0])
    return _lista_arquivos_anteriores


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


def nome_arquivo(_arquivo) -> str:
    """
    retira e retorna apenas o nome do arquivo da string da path
    :param _arquivo: str
    :return: str
    """
    return _arquivo.rsplit('/', 1)[1]


def tipo_arquivo(_arquivo: str) -> str:
    """
    retorna o tipo do arquivo baseado na extensao
    :param _arquivo: str
    :return: str
    """
    return (_arquivo.rsplit('.')[1]).lower()


def html_video(_arquivo: str) -> None:
    """
    cria o html para listar os videos no final do arquivo thumbs.html
    :param _arquivo: str
    :return: None
    """
    _arquivo_html = diretorio_destino(_arquivo) + '/thumbs.html'
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


def copia_arquivo(_arquivo: str) -> None:
    """
    copia o arquivo do sdcard para o diretório no disco
    :param _arquivo: str
    :return: None
    """
    destino = diretorio_destino(_arquivo) + tipo_arquivo(_arquivo)
    copy2(_arquivo, destino)


def cria_html_thumbs(_local_dos_arquivos: str, _nome_do_arquivo: str) -> None:
    """
    cria o html para exibir o conteudo dos diretorios criados
    :param _local_dos_arquivos: str
    :param _nome_do_arquivo: str
    :return: None
    """
    _arquivo_html = _local_dos_arquivos + 'thumbs.html'
    with open(_arquivo_html, 'a') as _arquivo:
        _arquivo.write(f"""
                <div style='padding:15px;'>
                    <p>
                        <a style='text-decoration: none' href='arw/{_nome_do_arquivo.replace('.JPG','.ARW')}'>
                            <strong style='font-family: "helvetica";font-size: 26px;'>
                                [ RAW ]
                            </strong>
                        </a>
                        &nbsp;&nbsp;
                        <a style='text-decoration: none' href='jpg/{_nome_do_arquivo}'>
                            <strong style='font-family: "helvetica";font-size: 26px;'>
                                [ JPG ]
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
    tamanho_thumbs = 900, 900
    local_de_salvamento = diretorio_destino(_arquivo) + 'thumbs/'
    nome_de_salvamento = (_arquivo.rsplit('/', 1))[1]
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
        for _arquivo in busca_arquivos(tipo):
            # busca todos os arquivos dos tipos declarados na lista no inicio do programa
            if not diretorio_existe(_arquivo):
                # cria os diretorios relativo a data das fotos e os subdiretorios para os tipos de arquivos
                cria_diretorios(_arquivo)
                # copia os arquivos para seus respectivos diretorios
            nome_do_arquivo = ((str(_arquivo).split('/'))[-1:])[0]
            if nome_do_arquivo not in busca_arquivos_anteriores():
                copia_arquivo(_arquivo)
                print(f'copiando arquivo {_arquivo}')
                if 'jpg' in tipo:
                    cria_thumbs(_arquivo)
                if 'mp4' in tipo:
                    html_video(_arquivo)
    print('FIM!')


executa_copia()

