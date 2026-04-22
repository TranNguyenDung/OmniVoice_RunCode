# OmniVoice - Hướng Dẫn Sử Dụng

## Giới thiệu

OmniVoice là model TTS (Text-to-Speech) hỗ trợ 600+ ngôn ngữ. Dự án này cung cấp 2 chức năng:

| Chức năng | Mục đích | Cách dùng |
|----------|----------|----------|
| **function_voice_generator** | Tạo các file audio mẫu theo mô tả giọng nói (Voice Design) | Không cần audio mẫu |
| **function_cloneaudio** | Tạo audio theo giọng của file audio mẫu (Voice Cloning) | Cần file audio mẫu |

---

## Cấu trúc thư mục

```
OmniVoice_RunCode/
├── function_voice_generator/      # Tạo audio Voice Design
│   ├── function_voice_generator.py
│   ├── text.txt                  # Text cần tạo audio
│   └── config_voices.txt       # Cấu hình giọng (instruct)
│
├── function_cloneaudio/          # Tạo audio Voice Cloning
│   ├── function_cloneaudio.py
│   ├── ref.wav                 # Audio mẫu (hoặc .mp3)
│   ├── text_ref.txt           # Transcript của audio mẫu
│   └── text.txt              # Text cần tạo audio
│
├── Models/                     # Model (tự tải)
└── Output/                   # Audio tạo ra
```

---

## Cài đặt

### 1. Cài Python dependencies

```bash
pip install torch==2.8.0 torchaudio==2.8.0
pip install omnivoice
pip install huggingface_hub
```

### 2. Chạy lần đầu

Model sẽ tự động tải về folder `Models/`.

Nếu chậm, thử:
```bash
export HF_ENDPOINT="https://hf-mirror.com"
```

---

## Cách sử dụng

### Voice Design: Tạo các file audio mẫu

Dùng để tạo các file audio mẫu theo mô tả giọng nói. Phù hợp khi bạn cần:
- Tạo nhiều giọng khác nhau (nam, nữ, trẻ, già...)
- Không có sẵn audio mẫu
- Thử nghiệm các giọng khác nhau

**Bước 1:** Sửa file `function_voice_generator/text.txt`

Mỗi dòng là một câu tạo ra một file audio riêng:
```
Xin chào các bạn.          # -> output_001.wav
Đây là bài test.        # -> output_002.wav
Chúc một ngày tốt lành!   # -> output_003.wav
```

**Bước 2:** Chọn giọng trong `function_voice_generator/config_voices.txt`

Mở file, bỏ `#` trước mẫu muốn dùng:
```
# MẪU ĐANG DÙNG
female, young adult      # <-- Bỏ # để dùng
```

Xem thêm các mẫu trong phần **Cấu hình giọng** bên dưới.

**Bước 3:** Chạy
```bash
python function_voice_generator/function_voice_generator.py
```

**Kết quả trong `Output/`:**
| File | Mô tả |
|------|-------|
| `output_001.wav` | Audio cho dòng 1 |
| `output_001_ref.txt` | Text của dòng 1 |
| `output_002.wav` | Audio cho dòng 2 |
| `output_002_ref.txt` | Text của dòng 2 |
| ... | ... |

---

### Voice Cloning: Tạo audio theo giọng mẫu

Dùng để tạo audio có giọng giống file audio mẫu. Phù hợp khi bạn:
- Có sẵn file audio mẫu cần nhân bản giọng
- Muốn tạo nhiều câu với cùng một giọng

**Bước 1:** Chuẩn bị audio mẫu

Đặt file vào `function_cloneaudio/`:
- Đặt tên: `ref.wav` hoặc `ref.mp3`

**Bước 2:** Sửa transcript của audio mẫu

Sửa file `function_cloneaudio/text_ref.txt` - nội dung mà người nói trong file audio:
```
Đây là nội dung file audio mẫu
```

**Bước 3:** Sửa text cần tạo

Sửa file `function_cloneaudio/text.txt`:
```
Xin chào các bạn.
Tôi đang test OmniVoice.
Chúc một ngày tốt lành!
```

**Bước 4:** Chạy
```bash
python function_cloneaudio/function_cloneaudio.py
```

**Kết quả trong `Output/`:**
| File | Mô tả |
|------|-------|
| `clone_20260422_181500.wav` | Audio gộp tất cả text |
| `clone_20260422_181500_list.txt` | Danh sách text gốc |

**Lưu ý:** Tất cả text trong text.txt sẽ được gộp thành một file audio duy nhất.

---

## Cấu hình giọng (Voice Design)

File `config_voices.txt` chứa các mẫu giọng. Mở file sẽ thấy:

### Mẫu đang dùng (dòng đầu tiên không có #)

```
female, young adult    # Nữ trẻ
```

### Một số mẫu phổ biến

| Instruct | Giọng |
|----------|-------|
| male | Nam |
| female | Nữ |
| male, young adult | Nam trẻ |
| male, middle-aged | Nam trung niên |
| male, elderly | Nam cao tuổi |
| male, low pitch | Nam giọng trầm |
| male, deep voice | Nam giọng trầm sâu |
| male, british accent | Nam giọng Anh |
| male, american accent | Nam giọng Mỹ |
| female, young adult | Nữ trẻ |
| female, middle-aged | Nữ trung niên |
| female, elderly | Nữ cao tuổi |
| female, high pitch | Nữ giọng cao |
| female, whisper | Nữ giọng thì thầm |
| female, british accent | Nữ giọng Anh |
| child | Trẻ em |
| teenager | Thiếu niên |

### Cách viết instruct

- Dùng dấu phẩy `,` ngăn cách các thuộc tính
- Có thể kết hợp nhiều thuộc tính
- Ví dụ: `female, young adult, high pitch, british accent`

---

## Xử lý sự cố

### Lỗi kết nối HuggingFace

```bash
export HF_ENDPOINT="https://hf-mirror.com"
```

### Kiểm tra model có tải chưa

```bash
ls Models/
```

Model đã tải sẽ có file `model_version.json`.

---

## Yêu cầu hệ thống

### Cấu hình tối thiểu (chạy được nhưng chậm)

- Python 3.8+
- RAM: 8GB
- GPU: 4GB VRAM (GTX 1650 / Quadro P2000 / RTX 3050)

### Cấu hình khuyến nghị

- RAM: 16GB
- GPU: 8GB+ VRAM (RTX 4070 / RTX 4080 / RTX 4090)

### Cấu hình hiện tại đã test

| Thông số | Giá trị |
|----------|---------|
| GPU | Quadro P2000 |
| VRAM | 4GB |
| Trạng thái | ✅ Chạy được |

---

## Khuyến nghị: Chạy bằng Google Colab

### Tại sao nên dùng Colab?

| So sánh | Laptop của bạn | Google Colab |
|---------|---------------|-------------|
| GPU | Quadro P2000 (4GB) | T4 (15GB), A100 (40GB) |
| VRAM | 4GB | 15GB-40GB |
| Tốc độ | Chậm | Nhanh |
| Miễn phí | ✅ | ✅ (với T4) |

### Cách chạy trên Colab

1. Mở https://colab.research.google.com
2. Tạo notebook mới
3. Chạy các lệnh sau:

```python
# Clone repo
!git clone https://github.com/TranNguyenDung/OmniVoice_RunCode.git
%cd OmniVoice_RunCode

# Cài đặt
!pip install torch==2.8.0 torchaudio==2.8.0
!pip install omnivoice huggingface_hub

# Chạy Voice Design
%cd function_voice_generator
!python function_voice_generator.py

# Hoặc chạy Voice Cloning
%cd ../function_cloneaudio
!python function_cloneaudio.py
```

4. Tải file audio từ folder `Output/` về máy

### Lưu ý khi dùng Colab

- Chọn GPU T4 (miễn phí) hoặc A100 (có phí)
- Runtime phải được kết nối để dùng GPU
- File trong Colab sẽ bị xóa khi runtime hết hạn, nhớ tải về ngay!