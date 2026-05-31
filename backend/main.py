import json
import re
import os
import io
from typing import List, Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from pypdf import PdfReader

app = FastAPI(title="CareerPilot AI API")

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JOB_ROLES_PATH = os.path.join(BASE_DIR, "data", "job_roles.json")

# Load job roles
def load_job_roles() -> Dict[str, List[str]]:
    try:
        with open(JOB_ROLES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {
            "Frontend Developer": ["HTML", "CSS", "JavaScript", "React", "TypeScript", "Git"],
            "Backend Developer": ["Python", "FastAPI", "SQL", "REST API", "Docker", "Git"],
            "Data Analyst": ["Python", "SQL", "Excel", "Power BI", "Statistics"],
            "AI/ML Engineer": ["Python", "Machine Learning", "TensorFlow", "Deep Learning", "Data Science"]
        }

JOB_ROLES = load_job_roles()

# Map all unique skills
ALL_SKILLS = sorted(list(set(skill for skills in JOB_ROLES.values() for skill in skills)))

# Precise regex patterns for each skill to avoid false positives and support variations
SKILL_PATTERNS = {
    "HTML": [r"\bhtml(?:5)?\b"],
    "CSS": [r"\bcss(?:3)?\b"],
    "JavaScript": [r"\bjavascript\b", r"\bjs\b"],
    "React": [r"\breact(?:\.js|js)?\b"],
    "TypeScript": [r"\btypescript\b", r"\bts\b"],
    "Git": [r"\bgit\b"],
    "Python": [r"\bpython\b"],
    "FastAPI": [r"\bfastapi\b", r"\bfast\s*api\b"],
    "SQL": [r"\bsql\b", r"\bmysql\b", r"\bpostgresql\b", r"\bsqlite\b", r"\bsql\s*server\b"],
    "REST API": [r"\brest\b", r"\brestapi\b", r"\brest\s*api(?:s)?\b", r"\brest-api(?:s)?\b", r"\brestful\s*api(?:s)?\b"],
    "Docker": [r"\bdocker\b"],
    "Excel": [r"\bexcel\b", r"\bmicrosoft\s*excel\b"],
    "Power BI": [r"\bpower\s*bi\b", r"\bpowerbi\b"],
    "Statistics": [r"\bstatistics\b", r"\bstatistical\b"],
    "Machine Learning": [r"\bmachine\s*learning\b", r"\bml\b"],
    "TensorFlow": [r"\btensorflow\b", r"\btf\b"],
    "Deep Learning": [r"\bdeep\s*learning\b"],
    "Data Science": [r"\bdata\s*science\b"]
}

# Study items for generating customized 4-week roadmaps
SKILL_STUDY_GUIDE = {
    "HTML": "Tìm hiểu Semantic HTML, thuộc tính accessibility (ARIA), SEO cơ bản và các form input.",
    "CSS": "Làm chủ Flexbox, CSS Grid, Responsive Design (Media Queries), và các CSS framework hiện đại.",
    "JavaScript": "Học về ES6+ syntax, xử lý bất đồng bộ (Promises, Async/Await), thao tác DOM, và Fetch API.",
    "React": "Nắm vững React Lifecycle, Hooks cơ bản (useState, useEffect, useContext) và cơ chế State Management.",
    "TypeScript": "Học static typing, interface, generic types, và cấu hình tsconfig cho dự án.",
    "Git": "Thực hành quy trình Git cơ bản: clone, branch, commit, pull request, merge và xử lý conflict.",
    "Python": "Nắm vững kiểu dữ liệu, OOP trong Python, List Comprehension, Generators và cách quản lý Virtual Environments.",
    "FastAPI": "Tìm hiểu cách tạo Endpoint, định nghĩa Pydantic Schema để validate dữ liệu, Dependency Injection và tối ưu API.",
    "SQL": "Học cách thiết kế cơ sở dữ liệu quan hệ, viết câu lệnh truy vấn nâng cao (JOINs, Group By), Indexing và Transactions.",
    "REST API": "Hiểu rõ các phương thức HTTP (GET, POST, PUT, DELETE), HTTP status codes, cơ chế authentication và cấu trúc JSON.",
    "Docker": "Học cách viết Dockerfile, build Docker Image, sử dụng Docker Compose để chạy ứng dụng đa container.",
    "Excel": "Làm chủ các hàm nâng cao (VLOOKUP, INDEX, MATCH), Pivot Tables và các kỹ thuật chuẩn hóa, làm sạch dữ liệu.",
    "Power BI": "Tìm hiểu kết nối dữ liệu, viết biểu thức DAX để tính toán, thiết kế biểu đồ trực quan tương tác nâng cao.",
    "Statistics": "Học thống kê mô tả, xác suất cơ bản, kiểm định giả thuyết (Hypothesis Testing) và các mô hình hồi quy tuyến tính.",
    "Machine Learning": "Tìm hiểu Supervised/Unsupervised Learning, sử dụng thư viện Scikit-Learn để train mô hình phân loại và hồi quy.",
    "TensorFlow": "Học cách xây dựng Neural Network cơ bản, làm quen với lớp Keras API và tối ưu hóa Hyperparameters.",
    "Deep Learning": "Tìm hiểu mạng nơ-ron tích chập (CNN) cho xử lý ảnh, mạng RNN/LSTM cho chuỗi dữ liệu, và lý thuyết Backpropagation.",
    "Data Science": "Làm chủ thư viện phân tích dữ liệu Pandas, NumPy và các công cụ trực quan hóa dữ liệu như Matplotlib/Seaborn."
}

class AnalyzeTextRequest(BaseModel):
    text: str

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Không thể giải mã file PDF: {str(e)}")

def perform_skills_gap_analysis(text: str) -> Dict[str, Any]:
    text_lower = text.lower()
    
    # 1. Detect skills
    detected_skills = []
    for skill in ALL_SKILLS:
        patterns = SKILL_PATTERNS.get(skill, [re.escape(skill.lower())])
        matched = False
        for pattern in patterns:
            if re.search(pattern, text_lower):
                matched = True
                break
        if matched:
            detected_skills.append(skill)
            
    # 2. Compare skills with each role and calculate match scores
    job_matches = []
    skill_gap = {}
    
    for role, required_skills in JOB_ROLES.items():
        matched_role_skills = [s for s in required_skills if s in detected_skills]
        missing_role_skills = [s for s in required_skills if s not in detected_skills]
        
        total_req = len(required_skills)
        score = (len(matched_role_skills) / total_req * 100) if total_req > 0 else 0
        
        job_matches.append({
            "role": role,
            "score": round(score, 1),
            "matchedCount": len(matched_role_skills),
            "totalCount": total_req
        })
        
        skill_gap[role] = {
            "matched": matched_role_skills,
            "missing": missing_role_skills
        }
    
    job_matches.sort(key=lambda x: x["score"], reverse=True)
    
    best_match = job_matches[0]
    best_role_name = best_match["role"]
    best_score = best_match["score"]
    
    best_missing = skill_gap[best_role_name]["missing"]
    roadmap = {}
    
    if not best_missing:
        roadmap = {
            "Week 1": {
                "title": "Tuần 1: Nghiên cứu Kiến trúc & Tối ưu hóa hệ thống",
                "focus": ["Nâng cao"],
                "content": f"Đi sâu vào kiến trúc nâng cao của {best_role_name}. Nghiên cứu thiết kế hệ thống có tính mở rộng cao và các design patterns thông dụng."
            },
            "Week 2": {
                "title": "Tuần 2: Xây dựng dự án thực tế quy mô lớn",
                "focus": ["Thực hành"],
                "content": "Thiết kế và triển khai một dự án cá nhân (Capstone Project) sử dụng toàn bộ skillset hiện có của bạn. Tập trung vào coding conventions và hiệu năng."
            },
            "Week 3": {
                "title": "Tuần 3: Tối ưu hóa Security & Quy trình kiểm thử",
                "focus": ["Security & Testing"],
                "content": "Tích hợp Unit Testing, Integration Testing và cấu hình bảo mật (OWASP top 10) cho hệ thống vừa xây dựng ở tuần 2."
            },
            "Week 4": {
                "title": "Tuần 4: Triển khai CI/CD & Chuẩn bị phỏng vấn tuyển dụng",
                "focus": ["Deployment & Jobs"],
                "content": "Thiết lập pipeline tự động hóa CI/CD, chuẩn bị portfolio trên GitHub, tối ưu CV và tham gia luyện tập các câu hỏi phỏng vấn hóc búa bậc Senior."
            }
        }
    else:
        num_missing = len(best_missing)
        weekly_skills = [[] for _ in range(4)]
        
        for idx, skill in enumerate(best_missing):
            week_idx = idx % 4
            weekly_skills[week_idx].append(skill)
            
        for i in range(4):
            week_key = f"Week {i+1}"
            skills_for_week = weekly_skills[i]
            
            if skills_for_week:
                title_skills = ", ".join(skills_for_week)
                roadmap[week_key] = {
                    "title": f"Tuần {i+1}: Học tập các kỹ năng thiếu ({title_skills})",
                    "focus": skills_for_week,
                    "content": "\n".join([f"- **{s}**: {SKILL_STUDY_GUIDE.get(s, 'Tìm hiểu sâu về công nghệ này.')}" for s in skills_for_week])
                }
            else:
                roadmap[week_key] = {
                    "title": f"Tuần {i+1}: Thực hành tích hợp & Luyện tập kỹ năng",
                    "focus": ["Thực hành", "Ôn tập"],
                    "content": f"Tập trung thực hành tích hợp các kỹ năng đã học ở tuần trước. Xây dựng mini-project để củng cố kiến thức thực tế cho vai trò {best_role_name}."
                }

    return {
        "extractedText": text,
        "detectedSkills": detected_skills,
        "jobMatches": job_matches,
        "bestRole": {
            "role": best_role_name,
            "score": best_score
        },
        "skillGap": skill_gap,
        "roadmap": roadmap
    }

@app.get("/job-roles")
def get_job_roles():
    """Returns the list of job roles and required skills."""
    return JOB_ROLES

@app.post("/analyze-text")
def analyze_text(request: AnalyzeTextRequest):
    """Analyzes a raw text string representing a CV."""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Nội dung văn bản CV không được để trống")
    return perform_skills_gap_analysis(request.text)

@app.post("/upload-cv")
async def upload_cv(file: UploadFile = File(...)):
    """Accepts a PDF CV file and performs the skills gap analysis."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Vui lòng chỉ tải lên file có định dạng PDF (.pdf)")
        
    try:
        contents = await file.read()
        extracted_text = extract_text_from_pdf_bytes(contents)
        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="Không thể trích xuất được văn bản từ file PDF. PDF có thể là file scan dạng ảnh hoặc bị mã hóa.")
        return perform_skills_gap_analysis(extracted_text)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống khi xử lý file CV: {str(e)}")

@app.get("/", response_class=HTMLResponse)
def get_demo_ui():
    """Serves the gorgeous interactive web app UI directly from the backend server."""
    return """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CareerPilot AI - Hệ Thống Phân Tích Khoảng Cách Kỹ Năng IT</title>
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🧭</text></svg>" />
    <!-- Google Fonts Inter -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Lucide Icons CDN -->
    <script src="https://unpkg.com/lucide@latest"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Inter', 'sans-serif'],
                    }
                }
            }
        }
    </script>
    <style>
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: #020617;
        }
        ::-webkit-scrollbar-thumb {
            background: #1e293b;
            border-radius: 9999px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #334155;
        }
        @keyframes pulseGlow {
            0%, 100% { opacity: 0.15; transform: scale(1); }
            50% { opacity: 0.3; transform: scale(1.05); }
        }
        .glowing-bg-accent {
            animation: pulseGlow 10s ease-in-out infinite;
        }
    </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen antialiased flex flex-col relative overflow-x-hidden font-sans">
    
    <!-- Aesthetic glowing background -->
    <div class="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] rounded-full bg-indigo-900/10 blur-[120px] pointer-events-none glowing-bg-accent"></div>
    <div class="absolute bottom-[-10%] right-[-10%] w-[600px] h-[600px] rounded-full bg-violet-900/10 blur-[150px] pointer-events-none glowing-bg-accent"></div>

    <!-- Header -->
    <header class="border-b border-slate-800/80 bg-slate-900/40 backdrop-blur-md sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between border-b border-slate-800/60 bg-slate-900/30 backdrop-blur-md sticky top-0 z-50">
            <div class="flex items-center space-x-3">
                <div class="p-2.5 bg-gradient-to-tr from-indigo-600 to-violet-600 rounded-xl shadow-lg shadow-indigo-500/20 text-white">
                    <i data-lucide="compass" class="h-6 w-6"></i>
                </div>
                <div>
                    <h1 class="text-xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-100 to-indigo-400 bg-clip-text text-transparent">
                        CareerPilot AI
                    </h1>
                    <p class="text-xs text-slate-400 hidden sm:block">
                        Hệ thống phân tích khoảng cách kỹ năng cho sinh viên IT
                    </p>
                </div>
            </div>
            <div class="text-xs px-3 py-1.5 rounded-full border border-indigo-500/20 bg-indigo-500/5 text-indigo-300 font-medium">
                Demo Bản MVP Chạy Thật
            </div>
        </div>
    </header>

    <!-- Main Container -->
    <main class="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8 z-10 flex flex-col gap-8">
        
        <!-- Pitch Hero Banner -->
        <div class="rounded-2xl border border-slate-800 bg-slate-900/30 p-6 flex flex-col md:flex-row md:items-center justify-between gap-6 shadow-xl">
            <div class="space-y-2 max-w-3xl">
                <div class="inline-flex items-center space-x-1.5 text-xs text-indigo-400 font-semibold uppercase tracking-wider">
                    <i data-lucide="sparkles" class="h-3.5 w-3.5"></i>
                    <span>Phân tích tự động</span>
                </div>
                <h2 class="text-2xl font-bold text-slate-100">
                    Định vị vị thế kỹ năng của bạn
                </h2>
                <p class="text-slate-400 text-sm leading-relaxed">
                    Tải CV định dạng PDF lên hoặc dán nội dung văn bản CV để đối chiếu với các yêu cầu kỹ năng chuẩn của các vị trí IT phổ biến (**Frontend**, **Backend**, **Data Analyst**, **AI/ML Engineer**). Hệ thống sẽ phát hiện kỹ năng tự động và xây dựng lộ trình học tập 4 tuần tối ưu nhất cho bạn.
                </p>
            </div>
            
            <!-- Quick Stats -->
            <div class="flex items-center gap-4 text-xs">
                <div class="bg-slate-900 border border-slate-800 rounded-xl p-3.5 text-center min-w-[90px] shadow-sm">
                    <div class="text-indigo-400 font-bold text-lg">4</div>
                    <div class="text-slate-400 mt-0.5">Vị trí IT</div>
                </div>
                <div class="bg-slate-900 border border-slate-800 rounded-xl p-3.5 text-center min-w-[90px] shadow-sm">
                    <div class="text-violet-400 font-bold text-lg">18</div>
                    <div class="text-slate-400 mt-0.5">Kỹ năng</div>
                </div>
                <div class="bg-slate-900 border border-slate-800 rounded-xl p-3.5 text-center min-w-[90px] shadow-sm">
                    <div class="text-emerald-400 font-bold text-lg">4 Tuần</div>
                    <div class="text-slate-400 mt-0.5">Lộ trình</div>
                </div>
            </div>
        </div>

        <!-- Dashboard Content Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
            
            <!-- Column Left: Input Zone -->
            <div class="lg:col-span-5 flex flex-col gap-6">
                
                <!-- Input Card -->
                <div class="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 flex flex-col gap-5 shadow-lg backdrop-blur-sm">
                    
                    <div class="flex items-center justify-between">
                        <h3 class="font-bold text-slate-100 flex items-center space-x-2 text-base">
                            <i data-lucide="file-text" class="h-5 w-5 text-indigo-400"></i>
                            <span>Cung cấp thông tin CV</span>
                        </h3>
                        <button id="btn-reset" class="text-xs text-rose-400 hover:text-rose-300 font-medium transition-colors hidden" onclick="resetForm()">
                            Xóa kết quả
                        </button>
                    </div>

                    <!-- Tabs Selector -->
                    <div class="flex bg-slate-950 p-1 rounded-xl border border-slate-800">
                        <button id="tab-pdf" onclick="switchTab('pdf')" class="flex-1 py-2 text-xs font-semibold rounded-lg bg-slate-800 text-slate-100 shadow transition-all">
                            Upload File PDF CV
                        </button>
                        <button id="tab-text" onclick="switchTab('text')" class="flex-1 py-2 text-xs font-semibold rounded-lg text-slate-400 hover:text-slate-200 transition-all">
                            Dán nội dung Văn Bản
                        </button>
                    </div>

                    <!-- Alert Box -->
                    <div id="error-box" class="p-3.5 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-300 text-xs flex items-start space-x-2.5 hidden">
                        <i data-lucide="alert-circle" class="h-4 w-4 shrink-0 mt-0.5"></i>
                        <span id="error-message"></span>
                    </div>

                    <!-- PDF Upload Zone -->
                    <div id="zone-pdf" class="border-2 border-dashed border-slate-800 hover:border-slate-700 bg-slate-950/20 rounded-xl p-8 text-center cursor-pointer transition-all flex flex-col items-center justify-center gap-3"
                         ondragover="onDragOver(event)" ondragleave="onDragLeave(event)" ondrop="onDrop(event)" onclick="triggerFileInput()">
                        <input type="file" id="cv-file" accept=".pdf" class="hidden" onchange="onFileSelected(event)">
                        <div id="upload-icon-container" class="p-3.5 rounded-full bg-slate-800/80 text-slate-400">
                            <i data-lucide="upload-cloud" class="h-6 w-6"></i>
                        </div>
                        <div id="upload-text-container" class="space-y-1">
                            <p class="text-sm font-medium text-slate-200">Kéo thả file PDF CV hoặc click để chọn</p>
                            <p class="text-xs text-slate-500">Chỉ hỗ trợ file PDF (.pdf) dung lượng tối đa 10MB</p>
                        </div>
                    </div>

                    <!-- Text Area Input Zone -->
                    <div id="zone-text" class="flex flex-col gap-2 hidden">
                        <textarea id="cv-text" rows="7" placeholder="Dán toàn bộ văn bản CV của bạn vào đây (Họ tên, kỹ năng, các dự án đã tham gia...)" 
                                  class="w-full bg-slate-950 border border-slate-800 rounded-xl p-3.5 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all resize-none font-sans leading-relaxed"></textarea>
                    </div>

                    <!-- Sample CV Selection -->
                    <div class="space-y-2.5">
                        <h4 class="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                            Dùng CV mẫu (Demo tức thì 🚀)
                        </h4>
                        <div class="flex flex-wrap gap-2" id="sample-cv-buttons">
                            <!-- Injected by JS -->
                        </div>
                    </div>

                    <!-- Trigger Button -->
                    <button id="btn-analyze" onclick="startAnalysis()" class="w-full py-3 rounded-xl font-semibold text-xs bg-indigo-600 hover:bg-indigo-500 text-white tracking-wide shadow-md flex items-center justify-center space-x-2 transition-all">
                        <i data-lucide="sparkles" class="h-4 w-4"></i>
                        <span id="btn-text">Phân tích CV PDF</span>
                    </button>

                </div>

                <!-- Job Standard Reference -->
                <div class="rounded-2xl border border-slate-800/80 bg-slate-900/30 p-6 flex flex-col gap-4">
                    <h3 class="font-bold text-sm text-slate-200 flex items-center space-x-2">
                        <i data-lucide="briefcase" class="h-4 w-4 text-violet-400"></i>
                        <span>Tiêu chuẩn kỹ năng (4 Vị trí)</span>
                    </h3>
                    <div class="divide-y divide-slate-800/50 space-y-3.5" id="roles-reference-list">
                        <!-- Injected by JS -->
                    </div>
                </div>

            </div>

            <!-- Column Right: Dashboard Results -->
            <div class="lg:col-span-7 flex flex-col gap-6" id="dashboard-right">
                
                <!-- Injected Empty State or Result Dashboard by JS -->
                <div class="h-full min-h-[380px] rounded-2xl border border-dashed border-slate-800 bg-slate-900/10 flex flex-col items-center justify-center text-center p-8 gap-5">
                    <div class="p-4 bg-slate-900 border border-slate-800 rounded-full text-slate-500 shadow-md">
                        <i data-lucide="compass" class="h-10 w-10 animate-spin-slow"></i>
                    </div>
                    <div class="max-w-md space-y-2">
                        <h4 class="font-bold text-slate-300 text-base">Chưa có dữ liệu phân tích</h4>
                        <p class="text-xs text-slate-500 leading-relaxed">
                            Vui lòng tải lên file PDF CV ở khung bên trái hoặc sử dụng nhanh một trong các **CV mẫu** để xem kết quả phân tích khoảng cách kỹ năng (skill gaps) cùng lộ trình học 4 tuần.
                        </p>
                    </div>
                    <div class="flex items-center space-x-2 text-[11px] text-slate-600 bg-slate-900/40 py-1.5 px-3 rounded-lg border border-slate-800">
                        <i data-lucide="sparkles" class="w-3.5 h-3.5 text-indigo-500"></i>
                        <span>Dễ dàng trình diễn trực tiếp trước giảng viên chấm điểm</span>
                    </div>
                </div>

            </div>

        </div>

    </main>

    <!-- Footer -->
    <footer class="border-t border-slate-900 bg-slate-950 mt-12 py-6 text-center text-xs text-slate-600">
        <div class="max-w-7xl mx-auto px-4">
            <p>© 2026 CareerPilot AI. Sản phẩm MVP demo phân tích khoảng cách kỹ năng dành cho sinh viên IT.</p>
        </div>
    </footer>

    <!-- App Logic Script -->
    <script>
        const SAMPLE_CVS = {
            frontend: {
                label: "CV Frontend mẫu",
                icon: "💻",
                text: `NGUYỄN VĂN A - FRONTEND DEVELOPER INTERN\\nHọc vấn: Sinh viên ngành Công nghệ thông tin - Đại học Bách Khoa.\\nKỹ năng: HTML, CSS, JavaScript, React, Git, Responsive Web Design.\\nDự án: Xây dựng Landing Page cá nhân bằng HTML5/CSS3, Ứng dụng Todo List quản lý công việc cá nhân bằng ReactJS và quản lý mã nguồn bằng Git.`
            },
            backend: {
                label: "CV Backend mẫu",
                icon: "⚙️",
                text: `TRẦN THỊ B - BACKEND DEVELOPER INTERN\\nHọc vấn: Sinh viên năm 3 ngành Khoa học Máy tính.\\nKỹ năng: Python, FastAPI, SQL, REST API, Git, Cơ sở dữ liệu PostgreSQL.\\nDự án: Thiết kế hệ thống API cho website thương mại điện tử mini bằng FastAPI, thực hành Docker hóa ứng dụng.`
            },
            data: {
                label: "CV Data Analyst mẫu",
                icon: "📊",
                text: `PHẠM VĂN C - DATA ANALYST ASPIRANT\\nKỹ năng chuyên môn: Python, SQL, Microsoft Excel nâng cao (VLOOKUP, Pivot Tables), Power BI dashboard, Statistics (Thống kê mô tả và suy diễn).\\nDự án: Phân tích dữ liệu hành vi người dùng và trực quan hóa báo cáo doanh số kinh doanh bằng SQL và Power BI.`
            },
            aiml: {
                label: "CV AI/ML mẫu",
                icon: "🧠",
                text: `LÊ VĂN D - AI/ML ENGINEER\\nKỹ năng: Python, Machine Learning, TensorFlow, Deep Learning, Data Science, Pandas, NumPy, Scikit-Learn.\\nDự án: Xây dựng và tối ưu mạng nơ-ron tích chập (CNN) phân loại hình ảnh vật nuôi bằng thư viện TensorFlow và Keras.`
            },
            empty: {
                label: "CV chưa khớp mẫu",
                icon: "📝",
                text: `NGUYỄN VĂN E - SINH VIÊN QUẢN TRỊ KINH DOANH\\nHọc vấn: Sinh viên chuyên ngành Quản trị thương mại.\\nKỹ năng mềm: Kỹ năng giao tiếp Tiếng Anh tốt, thuyết trình trước đám đông, kỹ năng đàm phán, làm việc nhóm, tin học văn phòng cơ bản (Word, PowerPoint).`
            }
        };

        let jobRoles = {};
        let activeTab = 'pdf';
        let selectedFile = null;
        let analysisResult = null;
        let selectedGapRole = '';

        // Initialize App
        window.addEventListener('DOMContentLoaded', async () => {
            await loadJobRoles();
            renderSampleButtons();
            lucide.createIcons();
        });

        async function loadJobRoles() {
            try {
                const res = await fetch('/job-roles');
                jobRoles = await res.json();
                renderRolesReference();
            } catch (err) {
                console.error("Failed to load roles:", err);
            }
        }

        function renderSampleButtons() {
            const container = document.getElementById('sample-cv-buttons');
            container.innerHTML = Object.entries(SAMPLE_CVS).map(([key, sample]) => `
                <button onclick="useSampleCV('${key}')" class="px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-950/40 hover:bg-slate-900 text-xs font-medium flex items-center space-x-1.5 transition-all text-slate-300 hover:text-slate-100 hover:border-slate-700">
                    <span class="text-sm">${sample.icon}</span>
                    <span>${sample.label}</span>
                </button>
            `).join('');
        }

        function renderRolesReference() {
            const container = document.getElementById('roles-reference-list');
            container.innerHTML = Object.entries(jobRoles).map(([role, skills]) => `
                <div class="pt-3.5 first:pt-0 flex flex-col gap-1.5">
                    <span class="text-xs font-bold text-indigo-300">${role}</span>
                    <div class="flex flex-wrap gap-1">
                        ${skills.map(s => `<span class="px-2 py-0.5 rounded bg-slate-950 text-[10px] text-slate-400 border border-slate-800">${s}</span>`).join('')}
                    </div>
                </div>
            `).join('');
        }

        function switchTab(tab) {
            activeTab = tab;
            setError('');
            
            const tabPdf = document.getElementById('tab-pdf');
            const tabText = document.getElementById('tab-text');
            const zonePdf = document.getElementById('zone-pdf');
            const zoneText = document.getElementById('zone-text');
            const btnText = document.getElementById('btn-text');

            if (tab === 'pdf') {
                tabPdf.className = "flex-1 py-2 text-xs font-semibold rounded-lg bg-slate-800 text-slate-100 shadow transition-all";
                tabText.className = "flex-1 py-2 text-xs font-semibold rounded-lg text-slate-400 hover:text-slate-200 transition-all";
                zonePdf.classList.remove('hidden');
                zoneText.classList.add('hidden');
                btnText.innerText = "Phân tích CV PDF";
            } else {
                tabText.className = "flex-1 py-2 text-xs font-semibold rounded-lg bg-slate-800 text-slate-100 shadow transition-all";
                tabPdf.className = "flex-1 py-2 text-xs font-semibold rounded-lg text-slate-400 hover:text-slate-200 transition-all";
                zoneText.classList.remove('hidden');
                zonePdf.classList.add('hidden');
                btnText.innerText = "Phân tích CV văn bản";
            }
        }

        function triggerFileInput() {
            document.getElementById('cv-file').click();
        }

        function onFileSelected(e) {
            const files = e.target.files;
            if (files && files.length > 0) {
                handleFile(files[0]);
            }
        }

        function handleFile(file) {
            setError('');
            if (file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf")) {
                selectedFile = file;
                
                const iconContainer = document.getElementById('upload-icon-container');
                const textContainer = document.getElementById('upload-text-container');
                const zonePdf = document.getElementById('zone-pdf');

                iconContainer.className = "p-3.5 rounded-full bg-emerald-500/10 text-emerald-400";
                zonePdf.className = "border-2 border-dashed border-emerald-500/40 bg-emerald-500/[0.01] rounded-xl p-8 text-center cursor-pointer transition-all flex flex-col items-center justify-center gap-3";
                textContainer.innerHTML = `
                    <p class="text-sm font-semibold text-slate-200 truncate max-w-[280px]">${file.name}</p>
                    <p class="text-xs text-slate-400">${(file.size / 1024).toFixed(1)} KB • Định dạng PDF</p>
                `;
            } else {
                setError("Chỉ chấp nhận file định dạng PDF (.pdf)");
            }
        }

        function onDragOver(e) {
            e.preventDefault();
            document.getElementById('zone-pdf').classList.add('border-indigo-500', 'bg-indigo-500/5');
        }

        function onDragLeave(e) {
            e.preventDefault();
            document.getElementById('zone-pdf').classList.remove('border-indigo-500', 'bg-indigo-500/5');
        }

        function onDrop(e) {
            e.preventDefault();
            document.getElementById('zone-pdf').classList.remove('border-indigo-500', 'bg-indigo-500/5');
            const files = e.dataTransfer.files;
            if (files && files.length > 0) {
                handleFile(files[0]);
            }
        }

        function setError(msg) {
            const box = document.getElementById('error-box');
            const txt = document.getElementById('error-message');
            if (msg) {
                txt.innerText = msg;
                box.classList.remove('hidden');
            } else {
                box.classList.add('hidden');
            }
        }

        function useSampleCV(key) {
            const sample = SAMPLE_CVS[key];
            document.getElementById('cv-text').value = sample.text.replace(/\\n/g, '\\n');
            switchTab('text');
            setError('');
            selectedFile = null;
            
            // Trigger analysis
            analyzeTextContent(sample.text.replace(/\\n/g, '\\n'));
        }

        async function startAnalysis() {
            setError('');
            if (activeTab === 'pdf') {
                if (!selectedFile) {
                    setError("Vui lòng chọn hoặc kéo thả file PDF CV của bạn.");
                    return;
                }
                analyzePDFFile();
            } else {
                const text = document.getElementById('cv-text').value;
                if (!text.trim()) {
                    setError("Vui lòng nhập hoặc dán nội dung văn bản CV trước.");
                    return;
                }
                analyzeTextContent(text);
            }
        }

        function setBtnLoading(loading) {
            const btn = document.getElementById('btn-analyze');
            const btnText = document.getElementById('btn-text');
            if (loading) {
                btn.disabled = true;
                btn.className = "w-full py-3 rounded-xl font-semibold text-xs bg-slate-800 text-slate-500 tracking-wide shadow-md flex items-center justify-center space-x-2 cursor-not-allowed";
                btnText.innerHTML = `
                    <div class="w-4 h-4 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin"></div>
                    <span>Đang phân tích CV...</span>
                `;
            } else {
                btn.disabled = false;
                btn.className = "w-full py-3 rounded-xl font-semibold text-xs bg-indigo-600 hover:bg-indigo-500 text-white tracking-wide shadow-md flex items-center justify-center space-x-2 transition-all";
                btnText.innerHTML = activeTab === 'pdf' ? 'Phân tích CV PDF' : 'Phân tích CV văn bản';
            }
        }

        async function analyzeTextContent(text) {
            setBtnLoading(true);
            try {
                const res = await fetch('/analyze-text', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text })
                });
                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || "Lỗi phân tích CV.");
                }
                analysisResult = await res.json();
                renderResults();
            } catch (err) {
                setError(err.message);
            } finally {
                setBtnLoading(false);
            }
        }

        async function analyzePDFFile() {
            setBtnLoading(true);
            try {
                const formData = new FormData();
                formData.append('file', selectedFile);
                
                const res = await fetch('/upload-cv', {
                    method: 'POST',
                    body: formData
                });
                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || "Lỗi xử lý file CV.");
                }
                analysisResult = await res.json();
                renderResults();
            } catch (err) {
                setError(err.message);
            } finally {
                setBtnLoading(false);
            }
        }

        function resetForm() {
            selectedFile = null;
            document.getElementById('cv-text').value = '';
            analysisResult = null;
            setError('');
            
            const iconContainer = document.getElementById('upload-icon-container');
            const textContainer = document.getElementById('upload-text-container');
            const zonePdf = document.getElementById('zone-pdf');
            
            iconContainer.className = "p-3.5 rounded-full bg-slate-800/80 text-slate-400";
            zonePdf.className = "border-2 border-dashed border-slate-800 hover:border-slate-700 bg-slate-950/20 rounded-xl p-8 text-center cursor-pointer transition-all flex flex-col items-center justify-center gap-3";
            textContainer.innerHTML = `
                <p class="text-sm font-medium text-slate-200">Kéo thả file PDF CV hoặc click để chọn</p>
                <p class="text-xs text-slate-500">Chỉ hỗ trợ file PDF (.pdf) dung lượng tối đa 10MB</p>
            `;
            
            document.getElementById('btn-reset').classList.add('hidden');
            
            document.getElementById('dashboard-right').innerHTML = `
                <div class="h-full min-h-[380px] rounded-2xl border border-dashed border-slate-800 bg-slate-900/10 flex flex-col items-center justify-center text-center p-8 gap-5">
                    <div class="p-4 bg-slate-900 border border-slate-800 rounded-full text-slate-500 shadow-md">
                        <i data-lucide="compass" class="h-10 w-10 animate-spin-slow"></i>
                    </div>
                    <div class="max-w-md space-y-2">
                        <h4 class="font-bold text-slate-300 text-base">Chưa có dữ liệu phân tích</h4>
                        <p class="text-xs text-slate-500 leading-relaxed font-sans">
                            Vui lòng tải lên file PDF CV ở khung bên trái hoặc sử dụng nhanh một trong các **CV mẫu** để xem kết quả phân tích khoảng cách kỹ năng (skill gaps) cùng lộ trình học 4 tuần.
                        </p>
                    </div>
                    <div class="flex items-center space-x-2 text-[11px] text-slate-600 bg-slate-900/40 py-1.5 px-3 rounded-lg border border-slate-800">
                        <i data-lucide="sparkles" class="w-3.5 h-3.5 text-indigo-500"></i>
                        <span>Dễ dàng trình diễn trực tiếp trước giảng viên chấm điểm</span>
                    </div>
                </div>
            `;
            lucide.createIcons();
        }

        function getProgressColorClass(score) {
            if (score >= 70) return 'bg-emerald-500';
            if (score >= 40) return 'bg-amber-500';
            return 'bg-rose-500';
        }

        function getProgressTextClass(score) {
            if (score >= 70) return 'text-emerald-400';
            if (score >= 40) return 'text-amber-400';
            return 'text-rose-400';
        }

        function onGapRoleChanged(roleName) {
            selectedGapRole = roleName;
            renderGapDetails();
        }

        function renderGapDetails() {
            const gapData = analysisResult.skillGap[selectedGapRole];
            const matchedContainer = document.getElementById('matched-skills-container');
            const missingContainer = document.getElementById('missing-skills-container');
            
            document.getElementById('matched-skills-title').innerText = `Kỹ năng đã có (${gapData.matched.length})`;
            document.getElementById('missing-skills-title').innerText = `Kỹ năng cần bổ sung (${gapData.missing.length})`;

            if (gapData.matched.length > 0) {
                matchedContainer.innerHTML = gapData.matched.map(s => `
                    <span class="px-2.5 py-1 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-[10px] font-semibold flex items-center space-x-1 shadow-sm">
                        <span>${s}</span>
                    </span>
                `).join('');
            } else {
                matchedContainer.innerHTML = `<span class="text-[11px] text-slate-600 italic">Chưa có kỹ năng nào được phát hiện cho vai trò này.</span>`;
            }

            if (gapData.missing.length > 0) {
                missingContainer.innerHTML = gapData.missing.map(s => `
                    <span class="px-2.5 py-1 rounded bg-rose-500/10 border border-rose-500/20 text-rose-300 text-[10px] font-semibold flex items-center space-x-1 shadow-sm animate-pulse">
                        <span>${s}</span>
                    </span>
                `).join('');
            } else {
                missingContainer.innerHTML = `<span class="text-[11px] text-emerald-500 font-semibold flex items-center space-x-1">🎉 <span>Hoàn toàn đáp ứng đủ kỹ năng yêu cầu!</span></span>`;
            }
        }

        function renderResults() {
            document.getElementById('btn-reset').classList.remove('hidden');
            selectedGapRole = analysisResult.bestRole.role;
            
            const colorClass = getProgressTextClass(analysisResult.bestRole.score);
            const offset = 2 * Math.PI * 40 * (1 - analysisResult.bestRole.score / 100);
            
            const detectedSkillsHtml = analysisResult.detectedSkills.length > 0 
                ? analysisResult.detectedSkills.map(s => `
                    <span class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-gradient-to-tr from-indigo-900/40 to-slate-900 text-indigo-200 border border-indigo-500/20 flex items-center space-x-1 shadow-sm">
                        <span class="w-1.5 h-1.5 rounded-full bg-indigo-400"></span>
                        <span>${s}</span>
                    </span>
                `).join('')
                : `<div class="text-xs text-slate-500 italic p-3 border border-slate-800/80 border-dashed rounded-xl text-center bg-slate-950/20 w-full">Không phát hiện thấy kỹ năng IT chuẩn nào trong CV.</div>`;

            const leaderboardHtml = analysisResult.jobMatches.map(m => `
                <div class="space-y-1.5">
                    <div class="flex justify-between items-center text-xs">
                        <span class="font-semibold text-slate-200">${m.role}</span>
                        <span class="font-bold ${getProgressTextClass(m.score)}">${m.score}% (${m.matchedCount}/${m.totalCount} kỹ năng)</span>
                    </div>
                    <div class="w-full bg-slate-950 h-2.5 rounded-full overflow-hidden border border-slate-900">
                        <div class="h-full rounded-full transition-all duration-500 ${getProgressColorClass(m.score)}" style="width: ${m.score}%"></div>
                    </div>
                </div>
            `).join('');

            const selectOptionsHtml = Object.keys(analysisResult.skillGap).map(r => `
                <option value="${r}" ${r === selectedGapRole ? 'selected' : ''}>${r}</option>
            `).join('');

            const roadmapHtml = Object.entries(analysisResult.roadmap).map(([week, data]) => {
                const weekVN = week === "Week 1" ? "Tuần 1" : week === "Week 2" ? "Tuần 2" : week === "Week 3" ? "Tuần 3" : "Tuần 4";
                return `
                    <div class="rounded-xl border border-slate-800/80 bg-slate-950/30 p-4.5 flex flex-col gap-2.5 hover:border-slate-750 transition-all hover:bg-slate-950/50 shadow-sm">
                        <div class="flex items-start justify-between gap-2 border-b border-slate-800 pb-2">
                            <span class="text-xs font-bold text-indigo-400 shrink-0 uppercase tracking-wide">${weekVN}</span>
                            <div class="flex flex-wrap justify-end gap-1">
                                ${data.focus.map(f => `<span class="px-1.5 py-0.5 rounded bg-slate-800 text-[9px] font-medium text-slate-400 border border-slate-750">${f}</span>`).join('')}
                            </div>
                        </div>
                        <div class="space-y-1.5 flex-1">
                            <h5 class="text-xs font-extrabold text-slate-200">${data.title}</h5>
                            <div class="text-[11px] text-slate-400 leading-relaxed whitespace-pre-line">${data.content}</div>
                        </div>
                    </div>
                `;
            }).join('');

            const container = document.getElementById('dashboard-right');
            container.innerHTML = `
                <div class="space-y-6">
                    
                    <!-- Score Hero Summary -->
                    <div class="rounded-2xl border border-slate-850 bg-gradient-to-tr from-slate-900 to-indigo-950/20 p-6 shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-6">
                        <div class="space-y-2.5">
                            <div class="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-xs text-indigo-300 font-semibold">
                                <i data-lucide="award" class="h-3.5 w-3.5"></i>
                                <span>Vị trí phù hợp nhất</span>
                            </div>
                            <div>
                                <h4 class="text-2xl font-extrabold text-white">${analysisResult.bestRole.role}</h4>
                                <p class="text-xs text-slate-400 mt-1">Dựa trên phân tích keyword matching trong văn bản CV của bạn</p>
                            </div>
                        </div>
                        <div class="flex items-center space-x-4 shrink-0">
                            <div class="relative flex items-center justify-center">
                                <svg class="w-24 h-24 transform -rotate-90">
                                    <circle cx="48" cy="48" r="40" stroke="currentColor" stroke-width="8" class="text-slate-800" fill="transparent" />
                                    <circle cx="48" cy="48" r="40" stroke="currentColor" stroke-width="8" class="${colorClass}" fill="transparent"
                                            stroke-dasharray="251.32" stroke-dashoffset="${offset}" />
                                </svg>
                                <div class="absolute text-center">
                                    <span class="text-xl font-extrabold ${colorClass}">${Math.round(analysisResult.bestRole.score)}%</span>
                                    <div class="text-[9px] text-slate-500 font-semibold tracking-wider uppercase">Match</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Detected Skills -->
                    <div class="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 flex flex-col gap-4 shadow-md">
                        <h4 class="font-bold text-sm text-slate-200 flex items-center space-x-2">
                            <i data-lucide="sparkles" class="h-4.5 w-4.5 text-indigo-400"></i>
                            <span>Kỹ năng phát hiện được (${analysisResult.detectedSkills.length})</span>
                        </h4>
                        <div class="flex flex-wrap gap-2">${detectedSkillsHtml}</div>
                    </div>

                    <!-- Leaderboard -->
                    <div class="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 flex flex-col gap-4 shadow-md">
                        <h4 class="font-bold text-sm text-slate-200 flex items-center space-x-2">
                            <i data-lucide="trending-up" class="h-4.5 w-4.5 text-violet-400"></i>
                            <span>Bảng xếp hạng độ phù hợp vị trí</span>
                        </h4>
                        <div class="space-y-4">${leaderboardHtml}</div>
                    </div>

                    <!-- Skill Gap Analysis -->
                    <div class="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 flex flex-col gap-4 shadow-md">
                        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
                            <h4 class="font-bold text-sm text-slate-200 flex items-center space-x-2">
                                <i data-lucide="check-circle-2" class="h-4.5 w-4.5 text-emerald-400"></i>
                                <span>Chi tiết khoảng cách kỹ năng (Skill Gap)</span>
                            </h4>
                            <select id="gap-role-select" onchange="onGapRoleChanged(this.value)" class="bg-slate-950 border border-slate-800 text-xs rounded-lg py-1 px-2.5 text-slate-300 focus:outline-none focus:border-indigo-500">
                                ${selectOptionsHtml}
                            </select>
                        </div>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-1">
                            <div class="space-y-3">
                                <div class="flex items-center space-x-1.5 text-xs font-semibold text-emerald-400">
                                    <i data-lucide="check-circle-2" class="h-4 w-4 shrink-0"></i>
                                    <span id="matched-skills-title">Kỹ năng đã có</span>
                                </div>
                                <div id="matched-skills-container" class="bg-slate-950/40 border border-slate-800/80 rounded-xl p-3.5 min-h-[100px] flex flex-wrap gap-1.5 content-start"></div>
                            </div>
                            <div class="space-y-3">
                                <div class="flex items-center space-x-1.5 text-xs font-semibold text-rose-400">
                                    <i data-lucide="x-circle" class="h-4 w-4 shrink-0"></i>
                                    <span id="missing-skills-title">Kỹ năng cần bổ sung</span>
                                </div>
                                <div id="missing-skills-container" class="bg-slate-950/40 border border-slate-800/80 rounded-xl p-3.5 min-h-[100px] flex flex-wrap gap-1.5 content-start"></div>
                            </div>
                        </div>
                    </div>

                    <!-- Roadmap -->
                    <div class="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 flex flex-col gap-4 shadow-md">
                        <div class="border-b border-slate-800 pb-3">
                            <h4 class="font-bold text-sm text-slate-200 flex items-center space-x-2">
                                <i data-lucide="calendar" class="h-4.5 w-4.5 text-indigo-400"></i>
                                <span>Lộ trình cải thiện trong 4 tuần (${analysisResult.bestRole.role})</span>
                            </h4>
                            <p class="text-xs text-slate-400 mt-1 leading-relaxed">
                                Lộ trình học tập chi tiết giúp bạn nhanh chóng bù đắp khoảng cách các kỹ năng còn thiếu của vai trò ${analysisResult.bestRole.role}.
                            </p>
                        </div>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">${roadmapHtml}</div>
                    </div>

                </div>
            `;
            
            renderGapDetails();
            lucide.createIcons();
        }
    </script>
</body>
</html>
"""
