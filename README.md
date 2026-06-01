# 💎 Jewelry Store — Full Stack AI Shopping Project

A full-stack jewelry e-commerce application with an integrated AI shopping assistant and semantic search.
Built across three separate projects that work together as one system.

---

## 🗂️ Project Structure

```
both/
├── פרויקט אנגולר -חנות תכשיטים/jewelryStore/   # Angular frontend
├── APIJewelryStore/                              # .NET backend API
└── ai_service/                                  # Python AI service
```

---

## 🔗 Original Repositories

### Angular Frontend
> **My project** — designed and developed independently

🔗 https://github.com/efratleibovitz/Jewelry-Srore-webSite

### .NET Backend API
> **Collaborative project** — developed together with a partner.
> I was an active collaborator on this repository, contributing to the architecture, controllers, services, and database layer.

🔗 https://github.com/Rachel37189/APIJewelryStore.git

### Python AI Service
> **My project** — built during the AI Shopping Agent workshop, added on top of the existing stack.
> This service is not in a separate repository — it lives alongside the other two projects.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Angular 18 (standalone components), PrimeNG |
| Backend | .NET 9, ASP.NET Core Web API, Entity Framework Core |
| AI Service | Python 3.14, FastAPI, OpenAI API |
| Database | SQL Server |
| AI Models | gpt-4o-mini (chat), text-embedding-3-small (search) |

---

## ✨ Features

### Store
- Browse jewelry by category (necklaces, rings, bracelets, earrings)
- Filter by color, style, price range
- Product detail pages with sizes
- Shopping cart and checkout
- User authentication and profile
- Order history
- Admin panel for products and orders

### AI Shopping Assistant 💬
- Floating chat bubble on every page
- Powered by GPT-4o-mini
- Knows your real products from the database
- Asks about budget before recommending
- Maintains conversation history
- Custom persona (Maya, jewelry stylist)

### Semantic Search 🔍
- Search icon in the header — opens a search dropdown
- Understands natural language: *"gold gift for mom"* finds relevant products even without exact keyword matches
- Uses OpenAI text embeddings (text-embedding-3-small)
- Embeddings are pre-computed at startup for instant search
- Clicking a result navigates directly to the product page

---

## 🚀 Running the Project Locally

### Prerequisites
- Node.js + Angular CLI
- .NET 9 SDK
- Python 3.10+
- SQL Server
- OpenAI API key with credits

### 1. Python AI Service
```bash
cd ai_service
pip install -r requirements.txt
# Edit .env and add your OpenAI API key
python -m uvicorn chat_service:app --port 8001 --reload
```

### 2. .NET API
Open `APIJewelryStore/WebApiShop.sln` in Visual Studio and run with IIS Express (F5).
Runs on `https://localhost:44320`.

### 3. Angular Frontend
```bash
cd "פרויקט אנגולר -חנות תכשיטים/jewelryStore"
npm install
ng serve
```
Open `http://localhost:4200`.

> ⚠️ Start in this order: Python → .NET → Angular

---

## 🤖 AI Service Architecture

```
Angular  →  .NET (secure proxy)  →  Python (FastAPI)  →  OpenAI
```

- Angular sends the user message to .NET
- .NET fetches real products from the DB and forwards everything to Python
- Python runs semantic search to find the top 5 relevant products
- Python calls OpenAI with the system prompt + relevant products + conversation history
- The reply comes back through .NET to Angular

The OpenAI API key never reaches the frontend — it lives only in the Python `.env` file.

---

## 📁 AI Service Files

```
ai_service/
├── chat_service.py   # FastAPI app — chat + search + embeddings
├── .env              # API key and store config (not committed to Git)
└── requirements.txt  # Python dependencies
```

---

## ⚙️ Environment Variables (ai_service/.env)

```
OPENAI_API_KEY=sk-proj-...
STORE_NAME=Jewelry Store
STORE_DESCRIPTION=We sell beautiful handcrafted jewelry...
```

> ⚠️ Never commit the `.env` file to Git.
