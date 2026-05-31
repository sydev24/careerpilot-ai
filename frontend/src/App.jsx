import React, { useState, useEffect } from 'react';
import {
  Compass,
  UploadCloud,
  FileText,
  Sparkles,
  CheckCircle2,
  XCircle,
  AlertCircle,
  ArrowRight,
  Calendar,
  TrendingUp,
  Briefcase,
  Award,
  BookOpen,
  ChevronRight
} from 'lucide-react';
import { fetchJobRoles, analyzeCVText, uploadCVFile } from './services/api';
import Header from './components/Header';

// Pre-defined high-quality sample CVs for instant demo
const SAMPLE_CVS = {
  frontend: {
    label: "CV Frontend mẫu",
    icon: "💻",
    text: `NGUYỄN VĂN A - FRONTEND DEVELOPER INTERN
Học vấn: Sinh viên ngành Công nghệ thông tin - Đại học Bách Khoa.
Kỹ năng: HTML, CSS, JavaScript, React, Git, Responsive Web Design.
Dự án: Xây dựng Landing Page cá nhân bằng HTML5/CSS3, Ứng dụng Todo List quản lý công việc cá nhân bằng ReactJS và quản lý mã nguồn bằng Git.`
  },
  backend: {
    label: "CV Backend mẫu",
    icon: "⚙️",
    text: `TRẦN THỊ B - BACKEND DEVELOPER INTERN
Học vấn: Sinh viên năm 3 ngành Khoa học Máy tính.
Kỹ năng: Python, FastAPI, SQL, REST API, Git, Cơ sở dữ liệu PostgreSQL.
Dự án: Thiết kế hệ thống API cho website thương mại điện tử mini bằng FastAPI, thực hành Docker hóa ứng dụng.`
  },
  data: {
    label: "CV Data Analyst mẫu",
    icon: "📊",
    text: `PHẠM VĂN C - DATA ANALYST ASPIRANT
Kỹ năng chuyên môn: Python, SQL, Microsoft Excel nâng cao (VLOOKUP, Pivot Tables), Power BI dashboard, Statistics (Thống kê mô tả và suy diễn).
Dự án: Phân tích dữ liệu hành vi người dùng và trực quan hóa báo cáo doanh số kinh doanh bằng SQL và Power BI.`
  },
  aiml: {
    label: "CV AI/ML mẫu",
    icon: "🧠",
    text: `LÊ VĂN D - AI/ML ENGINEER
Kỹ năng: Python, Machine Learning, TensorFlow, Deep Learning, Data Science, Pandas, NumPy, Scikit-Learn.
Dự án: Xây dựng và tối ưu mạng nơ-ron tích chập (CNN) phân loại hình ảnh vật nuôi bằng thư viện TensorFlow và Keras.`
  },
  empty: {
    label: "CV chưa khớp mẫu",
    icon: "📝",
    text: `NGUYỄN VĂN E - SINH VIÊN QUẢN TRỊ KINH DOANH
Học vấn: Sinh viên chuyên ngành Quản trị thương mại.
Kỹ năng mềm: Kỹ năng giao tiếp Tiếng Anh tốt, thuyết trình trước đám đông, kỹ năng đàm phán, làm việc nhóm, tin học văn phòng cơ bản (Word, PowerPoint).`
  }
};

export default function App() {
  const [jobRoles, setJobRoles] = useState({});
  const [activeInputTab, setActiveInputTab] = useState('pdf'); // 'pdf' or 'text'
  const [textInput, setTextInput] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [selectedGapRole, setSelectedGapRole] = useState('');
  const [dragOver, setDragOver] = useState(false);

  // Load Job Roles from Backend on Mount
  useEffect(() => {
    async function loadRoles() {
      try {
        const roles = await fetchJobRoles();
        setJobRoles(roles);
      } catch (err) {
        console.error("Lỗi tải thông tin vị trí IT từ backend:", err);
      }
    }
    loadRoles();
  }, []);

  // Update selected gap view role when result updates
  useEffect(() => {
    if (result && result.bestRole) {
      setSelectedGapRole(result.bestRole.role);
    }
  }, [result]);

  // Handle Drag & Drop events
  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    setError('');
    
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      const file = files[0];
      if (file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf")) {
        setSelectedFile(file);
        setActiveInputTab('pdf');
      } else {
        setError("Chỉ chấp nhận file định dạng PDF (.pdf)");
      }
    }
  };

  // Handle traditional file input
  const handleFileChange = (e) => {
    setError('');
    const files = e.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      if (file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf")) {
        setSelectedFile(file);
      } else {
        setError("Chỉ chấp nhận file định dạng PDF (.pdf)");
      }
    }
  };

  // Run analysis for PDF file
  const handleAnalyzePDF = async () => {
    if (!selectedFile) {
      setError("Vui lòng chọn hoặc kéo thả file PDF CV của bạn.");
      return;
    }

    setLoading(true);
    setError('');
    try {
      const data = await uploadCVFile(selectedFile);
      setResult(data);
    } catch (err) {
      setError(err.message || "Không thể phân tích file PDF. Vui lòng kiểm tra lại kết nối backend.");
    } finally {
      setLoading(false);
    }
  };

  // Run analysis for Text Input
  const handleAnalyzeText = async (textToAnalyze = textInput) => {
    const targetText = textToAnalyze || textInput;
    if (!targetText.trim()) {
      setError("Vui lòng nhập hoặc dán nội dung văn bản CV trước.");
      return;
    }

    setLoading(true);
    setError('');
    try {
      const data = await analyzeCVText(targetText);
      setResult(data);
    } catch (err) {
      setError(err.message || "Lỗi phân tích văn bản CV. Vui lòng thử lại.");
    } finally {
      setLoading(false);
    }
  };

  // Quickly trigger sample CV click
  const handleUseSample = (key) => {
    const sample = SAMPLE_CVS[key];
    setTextInput(sample.text);
    setActiveInputTab('text');
    setSelectedFile(null);
    setError('');
    
    // Auto trigger analysis
    handleAnalyzeText(sample.text);
  };

  // Clean current state
  const handleReset = () => {
    setSelectedFile(null);
    setTextInput('');
    setResult(null);
    setError('');
  };

  // Dynamic progress bar colors matching scores
  const getProgressColor = (score) => {
    if (score >= 70) return 'bg-emerald-500';
    if (score >= 40) return 'bg-amber-500';
    return 'bg-rose-500';
  };

  const getProgressTextColor = (score) => {
    if (score >= 70) return 'text-emerald-400';
    if (score >= 40) return 'text-amber-400';
    return 'text-rose-400';
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col relative overflow-hidden font-sans">
      
      {/* Aesthetic glowing background details */}
      <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] rounded-full bg-indigo-900/10 blur-[120px] pointer-events-none glowing-bg-accent"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[600px] h-[600px] rounded-full bg-violet-900/10 blur-[150px] pointer-events-none glowing-bg-accent"></div>

      {/* Header */}
      <Header />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8 z-10 flex flex-col gap-8">
        
        {/* Pitch Hero Banner */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/30 p-6 flex flex-col md:flex-row md:items-center justify-between gap-6 shadow-xl">
          <div className="space-y-2 max-w-3xl">
            <div className="inline-flex items-center space-x-1.5 text-xs text-indigo-400 font-semibold uppercase tracking-wider">
              <Sparkles className="h-3.5 w-3.5" />
              <span>Phân tích tự động</span>
            </div>
            <h2 className="text-2xl font-bold text-slate-100">
              Định vị vị thế kỹ năng của bạn
            </h2>
            <p className="text-slate-400 text-sm leading-relaxed">
              Tải CV định dạng PDF lên hoặc dán nội dung văn bản CV để đối chiếu với các yêu cầu kỹ năng chuẩn của các vị trí IT phổ biến (**Frontend**, **Backend**, **Data Analyst**, **AI/ML Engineer**). Hệ thống sẽ phát hiện kỹ năng tự động và xây dựng lộ trình học tập 4 tuần tối ưu nhất cho bạn.
            </p>
          </div>
          
          {/* Quick Stats Panel */}
          <div className="flex items-center gap-4 text-xs">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5 text-center min-w-[90px] shadow-sm">
              <div className="text-indigo-400 font-bold text-lg">4</div>
              <div className="text-slate-400 mt-0.5">Vị trí IT</div>
            </div>
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5 text-center min-w-[90px] shadow-sm">
              <div className="text-violet-400 font-bold text-lg">18</div>
              <div className="text-slate-400 mt-0.5">Kỹ năng</div>
            </div>
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5 text-center min-w-[90px] shadow-sm">
              <div className="text-emerald-400 font-bold text-lg">4 Tuần</div>
              <div className="text-slate-400 mt-0.5">Lộ trình</div>
            </div>
          </div>
        </div>

        {/* Dashboard Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Column Left: Input Zone */}
          <div className="lg:col-span-5 flex flex-col gap-6">
            
            {/* Input Card Container */}
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 flex flex-col gap-5 shadow-lg backdrop-blur-sm">
              
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-slate-100 flex items-center space-x-2 text-base">
                  <FileText className="h-5 w-5 text-indigo-400" />
                  <span>Cung cấp thông tin CV</span>
                </h3>
                {result && (
                  <button
                    onClick={handleReset}
                    className="text-xs text-rose-400 hover:text-rose-300 font-medium transition-colors"
                  >
                    Xóa kết quả
                  </button>
                )}
              </div>

              {/* Tabs */}
              <div className="flex bg-slate-950 p-1 rounded-xl border border-slate-800">
                <button
                  onClick={() => setActiveInputTab('pdf')}
                  className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all ${
                    activeInputTab === 'pdf'
                      ? 'bg-slate-800 text-slate-100 shadow'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Upload File PDF CV
                </button>
                <button
                  onClick={() => setActiveInputTab('text')}
                  className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all ${
                    activeInputTab === 'text'
                      ? 'bg-slate-800 text-slate-100 shadow'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Dán nội dung Văn Bản
                </button>
              </div>

              {/* Error Alert Box */}
              {error && (
                <div className="p-3.5 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-300 text-xs flex items-start space-x-2.5">
                  <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
                  <span>{error}</span>
                </div>
              )}

              {/* Tab Content: PDF */}
              {activeInputTab === 'pdf' && (
                <div
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all flex flex-col items-center justify-center gap-3 ${
                    dragOver
                      ? 'border-indigo-500 bg-indigo-500/5'
                      : selectedFile
                      ? 'border-emerald-500/40 bg-emerald-500/[0.01]'
                      : 'border-slate-800 hover:border-slate-700 bg-slate-950/20'
                  }`}
                >
                  <input
                    type="file"
                    id="cv-file-upload"
                    accept=".pdf"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                  <label htmlFor="cv-file-upload" className="cursor-pointer flex flex-col items-center gap-2">
                    <div className={`p-3.5 rounded-full ${
                      selectedFile ? 'bg-emerald-500/10 text-emerald-400' : 'bg-slate-800/80 text-slate-400'
                    }`}>
                      <UploadCloud className="h-6 w-6" />
                    </div>
                    {selectedFile ? (
                      <div className="space-y-1">
                        <p className="text-sm font-semibold text-slate-200 truncate max-w-[280px]">
                          {selectedFile.name}
                        </p>
                        <p className="text-xs text-slate-400">
                          {(selectedFile.size / 1024).toFixed(1)} KB • Định dạng PDF
                        </p>
                      </div>
                    ) : (
                      <div className="space-y-1">
                        <p className="text-sm font-medium text-slate-200">
                          Kéo thả file PDF CV hoặc click để chọn
                        </p>
                        <p className="text-xs text-slate-500">
                          Chỉ hỗ trợ file PDF (.pdf) dung lượng tối đa 10MB
                        </p>
                      </div>
                    )}
                  </label>
                </div>
              )}

              {/* Tab Content: Text Area */}
              {activeInputTab === 'text' && (
                <div className="flex flex-col gap-2">
                  <textarea
                    rows={7}
                    placeholder="Dán toàn bộ văn bản CV của bạn vào đây (Họ tên, kỹ năng, các dự án đã tham gia...)"
                    value={textInput}
                    onChange={(e) => setTextInput(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3.5 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all resize-none font-sans leading-relaxed"
                  />
                  <div className="text-[10px] text-slate-500 text-right">
                    Ký tự: {textInput.length}
                  </div>
                </div>
              )}

              {/* Sample CV Demo Selector */}
              <div className="space-y-2.5">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Dùng CV mẫu (Demo tức thì 🚀)
                </h4>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(SAMPLE_CVS).map(([key, sample]) => (
                    <button
                      key={key}
                      onClick={() => handleUseSample(key)}
                      className="px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-950/40 hover:bg-slate-900 text-xs font-medium flex items-center space-x-1.5 transition-all text-slate-300 hover:text-slate-100 hover:border-slate-700"
                    >
                      <span className="text-sm">{sample.icon}</span>
                      <span>{sample.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Analysis Trigger Button */}
              {activeInputTab === 'pdf' ? (
                <button
                  onClick={handleAnalyzePDF}
                  disabled={loading || !selectedFile}
                  className={`w-full py-3 rounded-xl font-semibold text-xs tracking-wide shadow-md flex items-center justify-center space-x-2 transition-all ${
                    loading
                      ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                      : !selectedFile
                      ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                      : 'bg-indigo-600 hover:bg-indigo-500 text-white hover:shadow-indigo-500/10'
                  }`}
                >
                  {loading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin"></div>
                      <span>Đang phân tích CV...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4" />
                      <span>Phân tích CV PDF</span>
                    </>
                  )}
                </button>
              ) : (
                <button
                  onClick={() => handleAnalyzeText()}
                  disabled={loading || !textInput.trim()}
                  className={`w-full py-3 rounded-xl font-semibold text-xs tracking-wide shadow-md flex items-center justify-center space-x-2 transition-all ${
                    loading
                      ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                      : !textInput.trim()
                      ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                      : 'bg-indigo-600 hover:bg-indigo-500 text-white hover:shadow-indigo-500/10'
                  }`}
                >
                  {loading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin"></div>
                      <span>Đang phân tích CV...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4" />
                      <span>Phân tích CV văn bản</span>
                    </>
                  )}
                </button>
              )}

            </div>

            {/* Standard Roles Reference Card */}
            <div className="rounded-2xl border border-slate-800/80 bg-slate-900/30 p-6 flex flex-col gap-4">
              <h3 className="font-bold text-sm text-slate-200 flex items-center space-x-2">
                <Briefcase className="h-4 w-4 text-violet-400" />
                <span>Tiêu chuẩn kỹ năng (4 Vị trí)</span>
              </h3>
              <div className="divide-y divide-slate-800/50 space-y-3.5">
                {Object.entries(jobRoles).map(([roleName, skills]) => (
                  <div key={roleName} className="pt-3.5 first:pt-0 flex flex-col gap-1.5">
                    <span className="text-xs font-bold text-indigo-300">{roleName}</span>
                    <div className="flex flex-wrap gap-1">
                      {skills.map(s => (
                        <span key={s} className="px-2 py-0.5 rounded bg-slate-950 text-[10px] text-slate-400 border border-slate-800">
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>

          {/* Column Right: Dashboard Results */}
          <div className="lg:col-span-7 flex flex-col gap-6">
            
            {result ? (
              <div className="space-y-6">
                
                {/* Score Hero Summary */}
                <div className="rounded-2xl border border-slate-850 bg-gradient-to-tr from-slate-900 to-indigo-950/20 p-6 shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-6">
                  
                  <div className="space-y-2.5">
                    <div className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-xs text-indigo-300 font-semibold">
                      <Award className="h-3.5 w-3.5" />
                      <span>Vị trí phù hợp nhất</span>
                    </div>
                    <div>
                      <h4 className="text-2xl font-extrabold text-white">
                        {result.bestRole.role}
                      </h4>
                      <p className="text-xs text-slate-400 mt-1">
                        Dựa trên phân tích keyword matching trong văn bản CV của bạn
                      </p>
                    </div>
                  </div>

                  {/* Circular / Dial Matching percentage visualizer */}
                  <div className="flex items-center space-x-4 shrink-0">
                    <div className="relative flex items-center justify-center">
                      <svg className="w-24 h-24 transform -rotate-90">
                        <circle
                          cx="48"
                          cy="48"
                          r="40"
                          stroke="currentColor"
                          strokeWidth="8"
                          className="text-slate-800"
                          fill="transparent"
                        />
                        <circle
                          cx="48"
                          cy="48"
                          r="40"
                          stroke="currentColor"
                          strokeWidth="8"
                          className={getProgressTextColor(result.bestRole.score)}
                          fill="transparent"
                          strokeDasharray={2 * Math.PI * 40}
                          strokeDashoffset={2 * Math.PI * 40 * (1 - result.bestRole.score / 100)}
                        />
                      </svg>
                      <div className="absolute text-center">
                        <span className={`text-xl font-extrabold ${getProgressTextColor(result.bestRole.score)}`}>
                          {Math.round(result.bestRole.score)}%
                        </span>
                        <div className="text-[9px] text-slate-500 font-semibold tracking-wider uppercase">Match</div>
                      </div>
                    </div>
                  </div>

                </div>

                {/* Detected Skills badges */}
                <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 flex flex-col gap-4 shadow-md">
                  <h4 className="font-bold text-sm text-slate-200 flex items-center space-x-2">
                    <Sparkles className="h-4.5 w-4.5 text-indigo-400" />
                    <span>Kỹ năng phát hiện được ({result.detectedSkills.length})</span>
                  </h4>
                  {result.detectedSkills.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {result.detectedSkills.map((skill) => (
                        <span
                          key={skill}
                          className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-gradient-to-tr from-indigo-900/40 to-slate-900 text-indigo-200 border border-indigo-500/20 flex items-center space-x-1 shadow-sm"
                        >
                          <span className="w-1.5 h-1.5 rounded-full bg-indigo-400"></span>
                          <span>{skill}</span>
                        </span>
                      ))}
                    </div>
                  ) : (
                    <div className="text-xs text-slate-500 italic p-3 border border-slate-800/80 border-dashed rounded-xl text-center bg-slate-950/20">
                      Không phát hiện thấy kỹ năng IT chuẩn nào trong CV.
                    </div>
                  )}
                </div>

                {/* Match Leaderboard */}
                <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 flex flex-col gap-4 shadow-md">
                  <h4 className="font-bold text-sm text-slate-200 flex items-center space-x-2">
                    <TrendingUp className="h-4.5 w-4.5 text-violet-400" />
                    <span>Bảng xếp hạng độ phù hợp vị trí</span>
                  </h4>
                  <div className="space-y-4">
                    {result.jobMatches.map((match) => (
                      <div key={match.role} className="space-y-1.5">
                        <div className="flex justify-between items-center text-xs">
                          <span className="font-semibold text-slate-200">{match.role}</span>
                          <span className={`font-bold ${getProgressTextColor(match.score)}`}>
                            {match.score}% ({match.matchedCount}/{match.totalCount} kỹ năng)
                          </span>
                        </div>
                        {/* Progress track */}
                        <div className="w-full bg-slate-950 h-2.5 rounded-full overflow-hidden border border-slate-900">
                          <div
                            className={`h-full rounded-full transition-all duration-500 ${getProgressColor(match.score)}`}
                            style={{ width: `${match.score}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Skill Gap Analysis Tab Panel */}
                <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 flex flex-col gap-4 shadow-md">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
                    <h4 className="font-bold text-sm text-slate-200 flex items-center space-x-2">
                      <CheckCircle2 className="h-4.5 w-4.5 text-emerald-400" />
                      <span>Chi tiết khoảng cách kỹ năng (Skill Gap)</span>
                    </h4>
                    
                    {/* Switch role dropdown */}
                    <select
                      value={selectedGapRole}
                      onChange={(e) => setSelectedGapRole(e.target.value)}
                      className="bg-slate-950 border border-slate-800 text-xs rounded-lg py-1 px-2.5 text-slate-300 focus:outline-none focus:border-indigo-500"
                    >
                      {Object.keys(result.skillGap).map((role) => (
                        <option key={role} value={role}>
                          {role}
                        </option>
                      ))}
                    </select>
                  </div>

                  {selectedGapRole && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-1">
                      
                      {/* Matched Skills */}
                      <div className="space-y-3">
                        <div className="flex items-center space-x-1.5 text-xs font-semibold text-emerald-400">
                          <CheckCircle2 className="h-4 w-4 shrink-0" />
                          <span>Kỹ năng đã có ({result.skillGap[selectedGapRole].matched.length})</span>
                        </div>
                        <div className="bg-slate-950/40 border border-slate-800/80 rounded-xl p-3.5 min-h-[100px] flex flex-wrap gap-1.5 content-start">
                          {result.skillGap[selectedGapRole].matched.length > 0 ? (
                            result.skillGap[selectedGapRole].matched.map((skill) => (
                              <span
                                key={skill}
                                className="px-2.5 py-1 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-[10px] font-semibold flex items-center space-x-1 shadow-sm"
                              >
                                <span>{skill}</span>
                              </span>
                            ))
                          ) : (
                            <span className="text-[11px] text-slate-600 italic">Chưa có kỹ năng nào được phát hiện cho vai trò này.</span>
                          )}
                        </div>
                      </div>

                      {/* Missing Skills */}
                      <div className="space-y-3">
                        <div className="flex items-center space-x-1.5 text-xs font-semibold text-rose-400">
                          <XCircle className="h-4 w-4 shrink-0" />
                          <span>Kỹ năng cần bổ sung ({result.skillGap[selectedGapRole].missing.length})</span>
                        </div>
                        <div className="bg-slate-950/40 border border-slate-800/80 rounded-xl p-3.5 min-h-[100px] flex flex-wrap gap-1.5 content-start">
                          {result.skillGap[selectedGapRole].missing.length > 0 ? (
                            result.skillGap[selectedGapRole].missing.map((skill) => (
                              <span
                                key={skill}
                                className="px-2.5 py-1 rounded bg-rose-500/10 border border-rose-500/20 text-[10px] font-semibold text-rose-300 flex items-center space-x-1 shadow-sm animate-pulse"
                              >
                                <span>{skill}</span>
                              </span>
                            ))
                          ) : (
                            <span className="text-[11px] text-emerald-500 font-semibold flex items-center space-x-1">
                              🎉 <span>Hoàn toàn đáp ứng đủ kỹ năng yêu cầu!</span>
                            </span>
                          )}
                        </div>
                      </div>

                    </div>
                  )}

                </div>

                {/* 4-Week Learning Roadmap */}
                <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 flex flex-col gap-4 shadow-md">
                  <div className="border-b border-slate-800 pb-3">
                    <h4 className="font-bold text-sm text-slate-200 flex items-center space-x-2">
                      <Calendar className="h-4.5 w-4.5 text-indigo-400" />
                      <span>Lộ trình cải thiện trong 4 tuần ({result.bestRole.role})</span>
                    </h4>
                    <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                      Lộ trình học tập chi tiết giúp bạn nhanh chóng bù đắp khoảng cách các kỹ năng còn thiếu của vai trò {result.bestRole.role}.
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
                    {Object.entries(result.roadmap).map(([weekKey, weekData]) => (
                      <div
                        key={weekKey}
                        className="rounded-xl border border-slate-800/80 bg-slate-950/30 p-4.5 flex flex-col gap-2.5 hover:border-slate-750 transition-all hover:bg-slate-950/50 shadow-sm"
                      >
                        <div className="flex items-start justify-between gap-2 border-b border-slate-800 pb-2">
                          <span className="text-xs font-bold text-indigo-400 shrink-0 uppercase tracking-wide">
                            {weekKey === "Week 1" ? "Tuần 1" : weekKey === "Week 2" ? "Tuần 2" : weekKey === "Week 3" ? "Tuần 3" : "Tuần 4"}
                          </span>
                          <div className="flex flex-wrap justify-end gap-1">
                            {weekData.focus.map((f) => (
                              <span
                                key={f}
                                className="px-1.5 py-0.5 rounded bg-slate-800 text-[9px] font-medium text-slate-400 border border-slate-750"
                              >
                                {f}
                              </span>
                            ))}
                          </div>
                        </div>

                        <div className="space-y-1.5 flex-1">
                          <h5 className="text-xs font-extrabold text-slate-200">
                            {weekData.title}
                          </h5>
                          <div className="text-[11px] text-slate-400 leading-relaxed whitespace-pre-line">
                            {weekData.content}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

              </div>
            ) : (
              
              /* Empty state placeholder when no CV is loaded */
              <div className="h-full min-h-[380px] rounded-2xl border border-dashed border-slate-800 bg-slate-900/10 flex flex-col items-center justify-center text-center p-8 gap-5">
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-full text-slate-500 shadow-md">
                  <Compass className="h-10 w-10 animate-spin-slow" />
                </div>
                <div className="max-w-md space-y-2">
                  <h4 className="font-bold text-slate-300 text-base">Chưa có dữ liệu phân tích</h4>
                  <p className="text-xs text-slate-500 leading-relaxed">
                    Vui lòng tải lên file PDF CV ở khung bên trái hoặc sử dụng nhanh một trong các **CV mẫu** để xem kết quả phân tích khoảng cách kỹ năng (skill gaps) cùng lộ trình học 4 tuần.
                  </p>
                </div>
                <div className="flex items-center space-x-2 text-[11px] text-slate-600 bg-slate-900/40 py-1.5 px-3 rounded-lg border border-slate-800">
                  <Sparkles className="w-3.5 h-3.5 text-indigo-500 animate-pulse" />
                  <span>Dễ dàng trình diễn trực tiếp trước giảng viên chấm điểm</span>
                </div>
              </div>

            )}

          </div>

        </div>

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 mt-12 py-6 text-center text-xs text-slate-600">
        <div className="max-w-7xl mx-auto px-4">
          <p>© 2026 CareerPilot AI. Sản phẩm MVP demo phân tích khoảng cách kỹ năng dành cho sinh viên IT.</p>
        </div>
      </footer>

    </div>
  );
}
