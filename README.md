# PUConnect 🫂

## 🤝 Sobre o projeto

Este projeto foi desenvolvido para a disciplina INF1039 - Aplicações Interativas da PUC-Rio. O site tem como objetivo divulgar eventos da universidade de forma mais clara e atrativa, facilitando a inscrição dos alunos e incentivando a participação. A plataforma permite visualizar, se inscrever e divulgar eventos, ajudando a aumentar o público nas atividades da PUC-Rio.

## 📝 Licença

MIT License

Copyright (c) [2025] [PUConnect]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Requisitos

- Python 3.8+
- Node.js 14+ (opcional, para desenvolvimento frontend)

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/PUConnect.git
cd PUConnect
```

2. Crie e ative um ambiente virtual Python:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências do backend:
```bash
pip install -r requirements.txt
```

4. (Opcional) Instale as dependências do frontend:
```bash
npm install
```

5. Configure o banco de dados:
```bash
python manage.py migrate
```

6. Crie um superusuário:
```bash
python manage.py createsuperuser
```

7. Execute o servidor de desenvolvimento:
```bash
python manage.py runserver
```

## Estrutura do Projeto

- `project/` - Diretório principal do projeto Django
  - `core/` - Aplicação principal
  - `config/` - Configurações do projeto
- `requirements.txt` - Dependências Python
- `package.json` - Dependências JavaScript (opcional)

## Dependências Principais

### Backend (Python)
- Django 5.1.1
- Django REST Framework 3.15.2
- Django CORS Headers 4.6.0
- Gunicorn 23.0.0
- PostgreSQL (psycopg2-binary 2.9.9)

### Frontend (JavaScript)
- Popper.js 2.11.8
