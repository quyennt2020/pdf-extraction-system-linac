# QUICK START GUIDE

## Bắt Đầu Nhanh (5 phút)

### 1. Cài Đặt Môi Trường
```bash
# Chạy script tự động (khuyến nghị)
.\setup.bat          # Windows
# hoặc
bash setup.sh        # Linux/Mac

# Hoặc cài đặt thủ công
python -m venv venv
venv\Scripts\activate     # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Khởi Động Server
```bash
# Sử dụng Makefile (khuyến nghị)
make run

# Hoặc chạy trực tiếp
cd backend
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Truy Cập Ứng Dụng
Mở trình duyệt và vào: http://localhost:8000

### 4. Kiểm Tra API
- Health Check: http://localhost:8000/health
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Workflow Sử Dụng

1. **Upload PDF** 📄
   - Kéo thả hoặc chọn file PDF
   - Hệ thống sẽ hiển thị preview

2. **Extract Entities** 🔍
   - Click "Process PDF"
   - Hệ thống tự động trích xuất entities

3. **Review Knowledge Graph** 🌐
   - Xem graph được tạo tự động
   - Interact với nodes và edges

4. **Edit & Refine** ✏️
   - Thêm/sửa/xóa entities
   - Tạo relationships mới
   - Merge duplicate entities

5. **Export Results** 💾
   - JSON format (cho developers)
   - RDF format (cho semantic web)
   - GraphML format (cho Gephi, NetworkX)

## Lệnh Thường Dùng

```bash
# Development
make dev           # Setup development environment
make run           # Start server
make test          # Run tests
make lint          # Check code quality
make format        # Format code

# Docker
make docker-build  # Build Docker image
make docker-run    # Run in container

# Utilities
make clean         # Clean cache files
make build         # Build package
make docs          # Build documentation
```

## Cấu Trúc Dữ Liệu

```
data/
├── graphs/        # Knowledge graphs (.json, .rdf, .graphml)
├── ontologies/    # Ontology models (.owl)
└── temp/          # Temporary processing files

uploads/           # Uploaded PDF files
logs/             # Application logs
```

## Troubleshooting

### Lỗi Thường Gặp

1. **Module not found**
   ```bash
   # Đảm bảo đang trong virtual environment
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **spaCy model not found**
   ```bash
   python -m spacy download en_core_web_sm
   ```

3. **Port 8000 đã được sử dụng**
   ```bash
   # Chạy trên port khác
   uvicorn backend.api.main:app --port 8001
   ```

4. **Permission denied**
   ```bash
   # Windows: Chạy terminal as Administrator
   # Linux/Mac: 
   chmod +x setup.sh
   ```

### Performance Tips

- Đối với PDF lớn (>50MB): Tăng `MAX_FILE_SIZE` trong `.env`
- Đối với nhiều entities: Tăng `MAX_NODES` và `MAX_EDGES`
- RAM thấp: Giảm `NLP_BATCH_SIZE` và `BATCH_SIZE`

## Next Steps

- Xem [README.md](README.md) để hiểu chi tiết về hệ thống
- Khám phá [API documentation](http://localhost:8000/docs)
- Tùy chỉnh cấu hình trong `.env`
- Viết custom extractors cho domain cụ thể

## Hỗ Trợ

- 📧 Email: tpump@example.com
- 🐛 Issues: GitHub Issues
- 📚 Docs: `/docs` folder
