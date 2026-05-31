# Pesquisa Perplexity — Full Equivalences (DB, Infra, Languages, UI, Patterns, Packages)

Pesquisa realizada em 31/05/2026. Cobre os 3 prompts finais para completar as tabelas do CodeDocs.

---

## Prompt 1: Database + Infra

### SQL Server → PostgreSQL
- Data types: 16 mapeamentos (VARCHAR, DATETIME2→TIMESTAMP, MONEY→NUMERIC, BIT→BOOLEAN, etc.)
- Syntax: 14 equivalências (TOP→LIMIT, GETDATE→NOW, ISNULL→COALESCE, IDENTITY→SERIAL, etc.)
- Stored Procedures: T-SQL→PL/pgSQL (70% automático, 30% manual)
- Tools: pgLoader (70-80% schema, 95% data), AWS SCT (60-70%), ora2pg, Ispirer SQLWays (85-90%)
- Queixa real: "200 procedures took 3 months to convert"

### IIS → Nginx/Caddy
- web.config → nginx.conf: URL rewrite, SSL, CORS, gzip, reverse proxy
- Caddy: automatic HTTPS, muito mais simples
- Queixa: "IIS URL Rewrite → Nginx rewrite is manual, no converter"

### Azure DevOps → GitHub Actions
- Pipeline YAML mapping: trigger, pool, steps, variables, secrets
- 80% cobertura com AI, 20% manual
- Secrets: Azure Key Vault → GitHub Secrets + OIDC

### .NET Framework → Docker
- Windows containers (10GB+) → .NET 8 Alpine (50MB)
- web.config → appsettings.json + env vars
- Best practice: pin exact version, never use :latest

### On-Premise → Cloud
- AWS: RDS, ECS/Fargate, S3, Managed AD
- Azure: SQL Database, App Service, Blob Storage, Entra ID
- Queixa: "ROW BY ROW migration is significantly slower than backup/restore"

---

## Prompt 2: More Source Languages

### Java Spring MVC → FastAPI/Express/NestJS
- 12 annotation mappings (@RestController, @GetMapping, @Autowired, etc.)
- Spring Data JPA → Prisma/SQLAlchemy/GORM: 10 mappings
- Thymeleaf/JSP → React/Vue/Angular: 6 mappings
- Accuracy: 85-95% safe
- Tools: OpenRewrite (95-99%), Moderne.io (90-95%)

### PHP Laravel → FastAPI/Express
- Eloquent → Prisma/SQLAlchemy: 11 mappings
- Blade → React/Vue: 8 mappings
- Middleware: 4 mappings
- Artisan → CLI: 2 mappings
- Tools: Rector (90-95%)
- Queixa: "Rector isn't AI, it's rule-based"

### Delphi → React/Blazor/Electron
- VCL/FMX → React: 12 component mappings
- BDE/ADO → Prisma/EF Core: 6 mappings
- DLL calls → REST/gRPC
- Accuracy: 65-75% (mais manual que Java/PHP)
- Queixa: "Migration ≠ Modernization"

### VB6 → React/Blazor
- Forms → React: 10 component mappings
- ADO/DAO → Prisma/EF Core: 6 mappings
- ActiveX → Web alternatives: 5 mappings (MSFlexGrid→AG Grid, MSChart→Chart.js)
- COM → REST/gRPC: 3 mappings
- Accuracy: 50-70% (mais manual de todas)
- Tools: Mobilize.Net (60-70%), VB Migration Partner (70-75%)
- Case study: airline VB6→React+.NET em 8 semanas, 60% automação

---

## Prompt 3: UI Libraries + Patterns + Packages

### UI Component Libraries
- DevExpress → MUI/AntDesign/PrimeReact: 12 mappings
- Telerik → Chakra/AntDesign/PrimeReact: 10 mappings
- Infragistics → AG Grid + Radix: 5 mappings
- ComponentOne → open source: 7 mappings
- SEM equivalente direto: Report Viewer, Scheduler, Ribbon, Pivot Grid

### Design Patterns
- Repository: C# → Python/Node/Go (6 métodos)
- Unit of Work: EF → Prisma/SQLAlchemy (5 operações)
- CQRS: MediatR → nestjs-cqrs/Python mediator (5 conceitos)
- DI: Microsoft.Extensions.DI → Depends/Injectable/Wire (4 lifetimes)
- Middleware: ASP.NET → Express/FastAPI/Gin (5 stages)

### Packages Adicionais (10 categorias novas)
- Email: SmtpClient → nodemailer/smtplib/gomail
- PDF: iTextSharp/QuestPDF → puppeteer-pdf/reportlab/gofpdf
- Excel: EPPlus/ClosedXML → exceljs/openpyxl/excelize
- Image: System.Drawing → sharp/Pillow/imaging
- File Storage: System.IO → fs/os/boto3
- Scheduling: Quartz.NET/Hangfire → node-cron/APScheduler/robfig-cron
- Real-Time: SignalR → Socket.io/WebSocket/gorilla-websocket
- Serialization: Newtonsoft.Json → pydantic/class-transformer/encoding-json

### Queixas mais comuns na migração
- Report Viewer: nenhum equivalente open source direto
- System.Drawing: Windows-only, crashes no Linux
- Scheduler: FullCalendar é $199/licença
- Ribbon: precisa custom implementation
