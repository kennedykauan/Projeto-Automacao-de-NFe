import os
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
from typing import Dict, Any
import logging

# Configuração de Logs Profissional
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class NFeProcessor:
    def __init__(self, namespaces: Dict[str, str] = None):
        # NFes utilizam namespaces no XML, precisamos mapeá-los
        self.ns = namespaces or {'ns': 'http://www.portalfiscal.inf.br/nfe'}

    def _get_text(self, root: Element, xpath: str) -> str:
        """Helper para extrair texto de um nó XML com segurança."""
        element = root.find(xpath, self.ns)
        return element.text if element is not None else ""

    def process_xml(self, file_path: str) -> Dict[str, Any]:
        """Lê o XML da NFe e extrai as informações críticas."""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Navegando pela estrutura padrão da NFe
            infNFe = root.find('.//ns:infNFe', self.ns)
            if infNFe is None:
                raise ValueError("Estrutura 'infNFe' não encontrada. O arquivo pode não ser uma NFe válida.")

            # Extração de Dados Cadastrais e Financeiros
            chave_acesso = infNFe.attrib.get('Id', '').replace('NFe', '')
            ide = infNFe.find('ns:ide', self.ns)
            emit = infNFe.find('ns:emit', self.ns)
            total = infNFe.find('ns:total/ns:ICMSTot', self.ns)

            data = {
                "chave_acesso": chave_acesso,
                "numero_nota": self._get_text(ide, 'ns:nNF'),
                "data_emissao": self._get_text(ide, 'ns:dhEmi'),
                "cnpj_emitente": self._get_text(emit, 'ns:CNPJ'),
                "nome_emitente": self._get_text(emit, 'ns:xNome'),
                "valor_total": float(self._get_text(total, 'ns:vNF') or 0.0),
                "valor_impostos": float(self._get_text(total, 'ns:vTotTrib') or 0.0)
            }

            logging.info(f"NFe {data['numero_nota']} processada com sucesso!")
            return data

        except Exception as e:
            logging.error(f"Erro ao processar o arquivo {file_path}: {str(e)}")
            raise


# Exemplo de Execução
if __name__ == "__main__":
    processor = NFeProcessor()

    # Para testar, basta colocar um arquivo .xml de NFe real ou mockado na mesma pasta
    xml_teste = "NFe_assinada.xml"

    if os.path.exists(xml_teste):
        dados_nota = processor.process_xml(xml_teste)
        print("\n--- Dados Extraídos ---")
        for k, v in dados_nota.items():
            print(f"{k.upper()}: {v}")
    else:
        logging.warning(f"Arquivo de teste '{xml_teste}' não encontrado. Crie um mock para testar.")