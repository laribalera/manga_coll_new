# 🧚  Manga Coll - V2 🧝‍♀️

Este repositório contém uma aplicação em construção para gerenciamento de uma coleção pessoal de mangás. 

## ⚙️ Funcionalidades

- Listagem da Coleção
- Adicionar volume
- Atualizar informações de um volume
- Deletar um volume

## 📑 Pré-requisitos

- Flask
- pymongo

  
## 🖥️ Instalação

1. Clone o repositório em sua máquina local:

    ```
    git clone https://github.com/baleralarissa/manga_coll_new.git
    ```

## 🖥️ Uso

- Utiliza dados de um database com três collections:
  
- `all_titles`
```
{
    "_id": {
    "$oid": ObjectID
    },
    "titulo": String,
    "volumes": int32,
    "vol_type": String,
    "author": String
}
```

- `all_volumes`
```
{
    "_id": {
      "$oid": ObjectID
    },
    "volume": int32,
    "titulo": String,
    "author": String,
    "status": String
  }
```
- `manga_details`.
```
{
   "_id": {
     "$oid": ObjectID
    },
   "filename": String,
   "image_id": {
       "$oid": ObjectID
    },
    "autor": String,
    "descricao": String,
    "lancamento": String,
    "titulo": String,
    "genero": String
}
``` 

## 🆗 Atualizações

- [x] Upload de nova versão do app com integração com MongoDB
- [x] Front end: Melhorar o visual da página
- [x] Modal de descrição da coleção
- [x] Novo visual index
- [x] Fazer upload de infos do form de nova coleção na tabela e retorna-las
- [X] Arrumar o andamento da coleção para aparecer zerado caso não hajam correspondencias
- [X] Front end: Criar novo formulario para alimentar tabela de resumo + tabela de volumes
- [X] Front end: Criar página de Volumes
- [x] Metodo delete aplicado para volumes e coleção
- [x] Update para volume
- [x] Ao deletar uma coleção, os volumes relacionados a ela também são deletados
- [x] Adicionar paginação na aba Volumes

## 🛠️ TO-DO

- [ ] Criar Update para as coleções
- [ ] Criar upload de sheets para preencher as infos
- [ ] Criar filtragem pela caixa de pesquisa
- [ ] Criar aba de estatisticas das coleções? (ainda pensando sobre)

## Autores

- @baleralarissa



