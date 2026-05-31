# CareerPilot AI

## Mô tả dự án

CareerPilot AI là hệ thống phân tích khoảng cách kỹ năng cho sinh viên IT.

Ứng dụng cho phép sinh viên upload CV, hệ thống sẽ trích xuất kỹ năng trong CV, so sánh với yêu cầu của các vị trí IT phổ biến, xác định kỹ năng còn thiếu và đề xuất lộ trình cải thiện trong 4 tuần.

Đây là bản MVP demo trong 2 tiếng, không cần đăng nhập, không cần database phức tạp, không cần thanh toán.

## Công nghệ sử dụng

### Frontend

* React
* Vite
* TailwindCSS

### Backend

* Python
* FastAPI

### Data

* JSON file

## Chức năng chính

1. Upload CV PDF
2. Trích xuất text từ CV
3. Phát hiện kỹ năng bằng keyword matching
4. So sánh kỹ năng với các vị trí IT
5. Tính điểm phù hợp theo phần trăm
6. Phân tích skill gap
7. Đề xuất vị trí phù hợp nhất
8. Tạo lộ trình học tập 4 tuần
9. Hiển thị kết quả trên dashboard

## Danh sách vị trí IT

### Frontend Developer

Yêu cầu:

* HTML
* CSS
* JavaScript
* React
* TypeScript
* Git

### Backend Developer

Yêu cầu:

* Python
* FastAPI
* SQL
* REST API
* Docker
* Git

### Data Analyst

Yêu cầu:

* Python
* SQL
* Excel
* Power BI
* Statistics

### AI/ML Engineer

Yêu cầu:

* Python
* Machine Learning
* TensorFlow
* Deep Learning
* Data Science

## Công thức tính điểm phù hợp

matchScore = số kỹ năng khớp / tổng số kỹ năng yêu cầu * 100

Ví dụ:

CV có:

* Python
* SQL
* Git

Backend Developer yêu cầu:

* Python
* FastAPI
* SQL
* REST API
* Docker
* Git

Điểm phù hợp:

3 / 6 * 100 = 50%

## API Backend

### POST /upload-cv

Nhận file PDF CV.

Trả về:

* extractedText
* detectedSkills
* jobMatches
* bestRole
* skillGap
* roadmap

### POST /analyze-text

Nhận text CV.

Trả về kết quả phân tích giống `/upload-cv`.

### GET /job-roles

Trả về danh sách vị trí và kỹ năng yêu cầu.

## Cấu trúc thư mục

careerpilot-ai/

* README.md
* frontend/

  * package.json
  * src/

    * App.jsx
    * components/
    * services/
* backend/

  * main.py
  * requirements.txt
  * data/

    * job_roles.json

## Giao diện

Dashboard gồm:

### Header

Tên hệ thống: CareerPilot AI

### Khu vực upload

* Upload file PDF
* Nút phân tích CV
* Nút dùng CV mẫu

### Khu vực kết quả

* Kỹ năng phát hiện được
* Bảng xếp hạng vị trí phù hợp
* Vị trí phù hợp nhất
* Skill gap
* Lộ trình học 4 tuần

## Yêu cầu UI

* Giao diện hiện đại
* Dùng card
* Dùng badge cho kỹ năng
* Dùng progress bar cho phần trăm phù hợp
* Responsive trên laptop và mobile
* Dễ demo trước giảng viên

## Giới hạn MVP

Không làm:

* Đăng nhập
* Phân quyền user
* Thanh toán
* Database phức tạp
* Crawl dữ liệu tuyển dụng thật
* AI pipeline phức tạp

Chỉ tập trung làm bản demo chạy được.

## Mục tiêu cuối cùng

Sau khi chạy ứng dụng, người dùng có thể:

1. Upload CV hoặc dùng CV mẫu
2. Bấm phân tích
3. Xem kỹ năng được phát hiện
4. Xem mình phù hợp với vị trí nào
5. Xem kỹ năng còn thiếu
6. Xem lộ trình cải thiện trong 4 tuần

Hãy xây dựng ứng dụng đúng theo README này.
